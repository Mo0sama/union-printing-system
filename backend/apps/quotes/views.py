import io
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.core.models import CompanySetting

from .forms import QuoteFilterForm, QuoteForm, QuoteItemFormSet
from .models import Quote


@login_required
@permission_required('quotes.view_quote', raise_exception=True)
def quote_list(request):
    queryset = Quote.objects.select_related(
        'customer', 'created_by'
    ).prefetch_related('items').all()
    filter_form = QuoteFilterForm(request.GET)

    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd.get('status'):
            queryset = queryset.filter(status=cd['status'])
        if cd.get('customer'):
            queryset = queryset.filter(
                customer__name__icontains=cd['customer']
            ) | queryset.filter(
                customer__company_name__icontains=cd['customer']
            ) | queryset.filter(
                customer__contact_person__icontains=cd['customer']
            )
        if cd.get('date_from'):
            queryset = queryset.filter(quote_date__gte=cd['date_from'])
        if cd.get('date_to'):
            queryset = queryset.filter(quote_date__lte=cd['date_to'])
        if cd.get('search'):
            queryset = queryset.filter(
                quote_number__icontains=cd['search']
            )

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'title': _('عروض الأسعار'),
    }
    return render(request, 'quotes/quote_list.html', context)


@login_required
@permission_required('quotes.view_quote', raise_exception=True)
def quote_detail(request, pk):
    quote = get_object_or_404(
        Quote.objects.select_related(
            'customer', 'created_by'
        ).prefetch_related('items'),
        pk=pk
    )
    context = {
        'quote': quote,
        'title': _('عرض سعر: %s') % quote.quote_number,
    }
    return render(request, 'quotes/quote_detail.html', context)


@login_required
@permission_required('quotes.add_quote', raise_exception=True)
def quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        formset = QuoteItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    quote = form.save(commit=False)
                    quote.created_by = request.user
                    quote.save()
                    formset.instance = quote
                    formset.save()
                    quote.calculate_totals()
                    quote.save()
                messages.success(request, _('تم إنشاء عرض السعر بنجاح'))
                return redirect('quotes:quote_detail', pk=quote.pk)
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء أدناه'))
    else:
        form = QuoteForm(initial={'valid_until': timezone.now().date() + timedelta(days=14)})
        formset = QuoteItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': _('إنشاء عرض سعر جديد'),
        'is_create': True,
    }
    return render(request, 'quotes/quote_form.html', context)


@login_required
@permission_required('quotes.change_quote', raise_exception=True)
def quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        formset = QuoteItemFormSet(request.POST, instance=quote)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    quote = form.save()
                    formset.save()
                    quote.calculate_totals()
                    quote.save()
                messages.success(request, _('تم تحديث عرض السعر بنجاح'))
                return redirect('quotes:quote_detail', pk=quote.pk)
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء أدناه'))
    else:
        form = QuoteForm(instance=quote)
        formset = QuoteItemFormSet(instance=quote)

    context = {
        'form': form,
        'formset': formset,
        'quote': quote,
        'title': _('تعديل عرض السعر: %s') % quote.quote_number,
        'is_create': False,
    }
    return render(request, 'quotes/quote_form.html', context)


@login_required
@permission_required('quotes.delete_quote', raise_exception=True)
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, _('تم حذف عرض السعر بنجاح'))
        return redirect('quotes:quote_list')
    context = {
        'quote': quote,
        'title': _('حذف عرض السعر'),
    }
    return render(request, 'quotes/quote_confirm_delete.html', context)


@login_required
@permission_required('quotes.change_quote', raise_exception=True)
def quote_convert_to_order(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if quote.status == Quote.Status.CONVERTED:
        messages.warning(request, _('تم تحويل عرض السعر إلى طلب مسبقاً'))
        return redirect('quotes:quote_detail', pk=pk)
    try:
        order = quote.convert_to_order()
        messages.success(
            request,
            _('تم تحويل عرض السعر إلى طلب رقم %s') % order.order_number
        )
        return redirect('orders:order_detail', pk=order.pk)
    except Exception as e:
        messages.error(request, _('حدث خطأ أثناء التحويل: %s') % str(e))
        return redirect('quotes:quote_detail', pk=pk)


@login_required
@permission_required('quotes.view_quote', raise_exception=True)
def quote_print_pdf(request, pk):
    quote = get_object_or_404(
        Quote.objects.prefetch_related('items').select_related('customer', 'created_by'),
        pk=pk
    )
    company = CompanySetting.get_settings()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=10*mm, leftMargin=10*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'ArabicTitle', parent=styles['Title'],
        fontName='Helvetica', alignment=1, spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        'ArabicNormal', parent=styles['Normal'],
        fontName='Helvetica', spaceAfter=6,
        alignment=2 if request.LANGUAGE_CODE == 'ar' else 0
    ))
    styles.add(ParagraphStyle(
        'ArabicHeader', parent=styles['Heading2'],
        fontName='Helvetica', spaceAfter=10,
        alignment=2 if request.LANGUAGE_CODE == 'ar' else 0
    ))

    elements = []

    if company.logo:
        img = Image(company.logo.path, width=60*mm, height=20*mm)
        elements.append(img)
    else:
        elements.append(Paragraph(company.company_name, styles['ArabicTitle']))

    elements.append(Spacer(1, 10*mm))
    header_data = [
        [_('رقم عرض السعر:'), quote.quote_number],
        [_('التاريخ:'), quote.quote_date.strftime('%Y-%m-%d')],
        [_('العميل:'), str(quote.customer)],
        [_('صلاحية حتى:'), quote.valid_until.strftime('%Y-%m-%d')],
    ]
    header_table = Table(header_data, colWidths=[80*mm, 100*mm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph(_('بنود عرض السعر'), styles['ArabicHeader']))

    items_data = [[_('#'), _('الوصف'), _('الكمية'), _('الوحدة'), _('سعر الوحدة'),
                   _('الخصم'), _('الإجمالي')]]
    for i, item in enumerate(quote.items.all(), 1):
        items_data.append([
            str(i), item.description, str(item.quantity), item.get_unit_display(),
            f'{item.unit_price:.2f}',
            f'{item.discount_percent:.1f}%' if item.discount_percent else '-',
            f'{item.total:.2f}',
        ])

    col_widths = [12*mm, 60*mm, 20*mm, 20*mm, 25*mm, 20*mm, 25*mm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.3, 0.6)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10*mm))

    totals_data = [
        [_('المجموع الفرعي:'), f'{quote.subtotal:.2f}'],
    ]
    if quote.discount_type:
        if quote.discount_type == 'percentage':
            totals_data.append([_('الخصم:'), f'{quote.discount_value:.1f}%'])
        else:
            totals_data.append([_('الخصم:'), f'{quote.discount_value:.2f}'])
    totals_data.append([_('الضريبة:'), f'{quote.tax_amount:.2f}'])
    totals_data.append([_('الإجمالي:'), f'{quote.total:.2f}'])

    totals_table = Table(totals_data, colWidths=[80*mm, 100*mm])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(totals_table)

    if quote.notes:
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(_('ملاحظات:'), styles['ArabicHeader']))
        elements.append(Paragraph(quote.notes, styles['ArabicNormal']))

    if quote.terms_conditions:
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(_('الشروط والأحكام:'), styles['ArabicHeader']))
        elements.append(Paragraph(quote.terms_conditions, styles['ArabicNormal']))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="quote-{quote.quote_number}.pdf"'
    )
    return response


@login_required
@permission_required('quotes.view_quote', raise_exception=True)
def quote_send_email(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    messages.info(
        request,
        _('سيتم إرسال عرض السعر %s عبر البريد الإلكتروني قريباً') % quote.quote_number
    )
    return redirect('quotes:quote_detail', pk=pk)
