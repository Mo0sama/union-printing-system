import json
import time

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.core.models import CompanySetting

from .forms import ClientRegistrationForm, QuoteSaveForm
from .models import (
    CalculatorQuote, CalculatorQuoteItem, GiveawayCategory,
    GiveawayPricingTier, GiveawayProduct, PricingTier,
    ServiceCategory, ServiceProduct,
)


def calculator_home(request):
    service_categories = ServiceCategory.objects.filter(is_active=True)
    giveaway_categories = GiveawayCategory.objects.filter(is_active=True)
    context = {
        'service_categories': service_categories,
        'giveaway_categories': giveaway_categories,
        'title': _('حاسبة الأسعار'),
    }
    return render(request, 'calculator/calculator_home.html', context)


def printing_calculator(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('products__pricing_tiers')
    context = {
        'categories': categories,
        'title': _('حاسبة الطباعة'),
    }
    return render(request, 'calculator/printing_calculator.html', context)


def giveaway_calculator(request):
    categories = GiveawayCategory.objects.filter(is_active=True).prefetch_related(
        'products__options', 'products__pricing_tiers'
    )
    context = {
        'categories': categories,
        'title': _('حاسبة الهدايا الدعائية'),
    }
    return render(request, 'calculator/giveaway_calculator.html', context)


def api_calculate(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    calc_type = data.get('type', 'printing')
    items_data = data.get('items', [])
    tax_percent = float(data.get('tax_percent', 14))

    client_discount = 0
    if request.user.is_authenticated and request.user.role == User.Role.CLIENT:
        client_discount = float(request.user.client_discount_percent or 0)

    calculated_items = []
    subtotal = 0

    for item in items_data:
        product_id = item.get('product_id')
        quantity = int(item.get('quantity', 0))
        option_id = item.get('option_id')

        if quantity < 1:
            continue

        if calc_type == 'printing':
            product = get_object_or_404(ServiceProduct, id=product_id, is_active=True)
            unit_price = float(product.get_price_for_quantity(quantity))
            category_name = product.category.name_ar
            product_name = product.name_ar
            option_name = ''
        else:
            product = get_object_or_404(GiveawayProduct, id=product_id, is_active=True)
            unit_price = float(product.get_price_for_quantity(quantity, option_id))
            category_name = product.category.name_ar
            product_name = product.name_ar
            option_name = ''
            if option_id:
                option = product.options.filter(id=option_id).first()
                if option:
                    unit_price += float(option.price_adjustment)
                    option_name = option.name_ar

        line_total = unit_price * quantity
        subtotal += line_total

        calculated_items.append({
            'category_name': category_name,
            'product_name': product_name,
            'option_name': option_name,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'line_total': round(line_total, 2),
        })

    discount_amount = subtotal * (client_discount / 100)
    after_discount = subtotal - discount_amount
    tax_amount = after_discount * (tax_percent / 100)
    total = after_discount + tax_amount

    company = CompanySetting.get_settings()

    return JsonResponse({
        'items': calculated_items,
        'subtotal': round(subtotal, 2),
        'client_discount_percent': client_discount,
        'discount_amount': round(discount_amount, 2),
        'tax_percent': tax_percent,
        'tax_amount': round(tax_amount, 2),
        'total': round(total, 2),
        'currency': company.currency,
    })


@require_POST
def save_quote(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    calc_type = data.get('type', 'printing')
    items_data = data.get('items', [])
    tax_percent = float(data.get('tax_percent', 14))
    contact_name = data.get('contact_name', '').strip()
    contact_email = data.get('contact_email', '').strip()
    contact_phone = data.get('contact_phone', '').strip()
    company = data.get('company', '').strip()
    notes = data.get('notes', '').strip()

    if not contact_name or not contact_email or not contact_phone:
        return JsonResponse({'error': 'الاسم والبريد الإلكتروني ورقم الهاتف مطلوبون'}, status=400)

    if not items_data:
        return JsonResponse({'error': 'يجب إضافة منتج واحد على الأقل'}, status=400)

    client_discount = 0
    user = request.user if request.user.is_authenticated else None
    if user and user.role == User.Role.CLIENT:
        client_discount = float(user.client_discount_percent or 0)

    with transaction.atomic():
        quote = CalculatorQuote(
            user=user,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            company=company,
            quote_type=calc_type,
            discount_percent=client_discount,
            tax_percent=tax_percent,
            notes=notes,
            status=CalculatorQuote.Status.SUBMITTED,
        )
        quote.save()

        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            option_id = item.get('option_id')

            if quantity < 1:
                continue

            if calc_type == 'printing':
                product = ServiceProduct.objects.filter(id=product_id, is_active=True).first()
                if not product:
                    continue
                unit_price = float(product.get_price_for_quantity(quantity))
                category_name = product.category.name_ar
                product_name = product.name_ar
                option_name = ''
            else:
                product = GiveawayProduct.objects.filter(id=product_id, is_active=True).first()
                if not product:
                    continue
                unit_price = float(product.get_price_for_quantity(quantity, option_id))
                category_name = product.category.name_ar
                product_name = product.name_ar
                option_name = ''
                if option_id:
                    option = product.options.filter(id=option_id).first()
                    if option:
                        unit_price += float(option.price_adjustment)
                        option_name = option.name_ar

            line_total = unit_price * quantity

            CalculatorQuoteItem.objects.create(
                quote=quote,
                product_type=CalculatorQuoteItem.ProductType.SERVICE if calc_type == 'printing' else CalculatorQuoteItem.ProductType.GIVEAWAY,
                category_name=category_name,
                product_name=product_name,
                option_name=option_name,
                quantity=quantity,
                unit_price=round(unit_price, 2),
                line_total=round(line_total, 2),
            )

        quote.calculate_totals()
        quote.save()

    return JsonResponse({
        'success': True,
        'quote_id': quote.id,
        'quote_number': quote.quote_number,
    })


def client_register(request):
    if request.user.is_authenticated:
        return redirect('calculator:calculator_home')

    last_reg = request.session.get('last_registration_time', 0)
    if time.time() - last_reg < 300:
        messages.error(request, _('يمكنك إنشاء حساب جديد مرة واحدة كل 5 دقائق'))
        return redirect('calculator:calculator_home')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['last_registration_time'] = time.time()
            messages.success(request, _('تم إنشاء الحساب بنجاح! مرحباً بك!'))
            return redirect('calculator:calculator_home')
    else:
        form = ClientRegistrationForm()

    context = {
        'form': form,
        'title': _('تسجيل عميل جديد'),
    }
    return render(request, 'calculator/client_register.html', context)


@login_required
def my_quotes(request):
    if request.user.role != User.Role.CLIENT:
        messages.warning(request, _('هذه الصفحة مخصصة للعملاء فقط'))
        return redirect('calculator:calculator_home')

    quotes = CalculatorQuote.objects.filter(user=request.user)
    context = {
        'quotes': quotes,
        'title': _('عروض أسعاري'),
    }
    return render(request, 'calculator/my_quotes.html', context)


@login_required
def my_quote_detail(request, pk):
    quote = get_object_or_404(CalculatorQuote, pk=pk, user=request.user)
    context = {
        'quote': quote,
        'company': CompanySetting.get_settings(),
        'title': _('عرض سعر: %s') % quote.quote_number,
    }
    return render(request, 'calculator/my_quote_detail.html', context)
