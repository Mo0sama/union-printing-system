from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Sum, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.orders.models import Order
from apps.pos.models import POSSale
from apps.inventory.models import InventoryValuation

from .models import Account, JournalEntry, JournalLine


@login_required
@permission_required('accounting.view_account', raise_exception=True)
def chart_of_accounts(request):
    accounts = Account.objects.filter(parent__isnull=True).prefetch_related('children__children')
    context = {
        'accounts': accounts,
        'title': 'دليل الحسابات',
    }
    return render(request, 'accounting/chart_of_accounts.html', context)


@login_required
@permission_required('accounting.view_journalentry', raise_exception=True)
def journal_entry_list(request):
    entries = JournalEntry.objects.select_related('created_by').all().order_by('-entry_date', '-id')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status:
        entries = entries.filter(status=status)
    if date_from:
        entries = entries.filter(entry_date__gte=date_from)
    if date_to:
        entries = entries.filter(entry_date__lte=date_to)

    context = {
        'entries': entries,
        'title': 'القيود المحاسبية',
    }
    return render(request, 'accounting/journal_entry_list.html', context)


@login_required
@permission_required('accounting.change_journalentry', raise_exception=True)
def journal_entry_detail(request, pk):
    entry = get_object_or_404(
        JournalEntry.objects.select_related('created_by'),
        pk=pk
    )
    lines = entry.lines.select_related('account').all()
    context = {
        'entry': entry,
        'lines': lines,
        'title': f'قيد: {entry.entry_number}',
    }
    return render(request, 'accounting/journal_entry_detail.html', context)


@login_required
@permission_required('accounting.add_journalentry', raise_exception=True)
def journal_entry_create(request):
    if request.method == 'POST':
        entry_date_str = request.POST.get('entry_date')
        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            entry_date = timezone.now().date()
        description = request.POST.get('description')
        accounts = request.POST.getlist('account')
        debits = request.POST.getlist('debit')
        credits = request.POST.getlist('credit')
        descriptions = request.POST.getlist('line_description')

        total_debit = sum(float(d or 0) for d in debits)
        total_credit = sum(float(c or 0) for c in credits)

        if abs(total_debit - total_credit) > 0.01:
            messages.error(request, 'القيد غير متوازن: يجب أن يتساوى مجموع الطرفين')
            return redirect('accounting:journal_entry_create')

        try:
            with transaction.atomic():
                entry = JournalEntry.objects.create(
                    entry_date=entry_date,
                    description=description,
                    created_by=request.user,
                    status='posted',
                    posted_at=timezone.now(),
                )
                for i, account_id in enumerate(accounts):
                    if not account_id:
                        continue
                    debit = float(debits[i] or 0)
                    credit = float(credits[i] or 0)
                    if debit == 0 and credit == 0:
                        continue
                    JournalLine.objects.create(
                        entry=entry,
                        account_id=account_id,
                        debit=debit,
                        credit=credit,
                        description=descriptions[i] if i < len(descriptions) else '',
                    )
            messages.success(request, f'تم إنشاء القيد {entry.entry_number} بنجاح')
            return redirect('accounting:journal_entry_detail', pk=entry.pk)
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return redirect('accounting:journal_entry_create')

    accounts = Account.objects.filter(is_active=True).order_by('code')
    context = {
        'accounts': accounts,
        'title': 'قيد محاسبي جديد',
        'today': timezone.now().date(),
    }
    return render(request, 'accounting/journal_entry_form.html', context)


@login_required
@permission_required('accounting.view_account', raise_exception=True)
def profit_loss_report(request):
    date_from = request.GET.get('date_from', str(date.today().replace(day=1)))
    date_to = request.GET.get('date_to', str(date.today()))

    income_accounts = Account.objects.filter(
        account_type='income', is_active=True
    ).order_by('code')
    expense_accounts = Account.objects.filter(
        account_type='expense', is_active=True
    ).order_by('code')

    def get_balance(account, from_date, to_date):
        lines = JournalLine.objects.filter(
            account=account,
            entry__entry_date__gte=from_date,
            entry__entry_date__lte=to_date,
            entry__status='posted',
        )
        debits = lines.aggregate(total=Coalesce(Sum('debit'), Value(0), output_field=DecimalField()))['total']
        credits = lines.aggregate(total=Coalesce(Sum('credit'), Value(0), output_field=DecimalField()))['total']
        return credits - debits

    income_data = []
    total_income = 0
    for acc in income_accounts:
        bal = get_balance(acc, date_from, date_to)
        if bal != 0:
            income_data.append({'account': acc, 'balance': bal})
            total_income += bal

    expense_data = []
    total_expense = 0
    for acc in expense_accounts:
        bal = get_balance(acc, date_from, date_to)
        if bal != 0:
            expense_data.append({'account': acc, 'balance': bal})
            total_expense += bal

    net_profit = total_income - total_expense

    context = {
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'قائمة الأرباح والخسائر',
    }
    return render(request, 'accounting/profit_loss.html', context)


@login_required
@permission_required('accounting.view_account', raise_exception=True)
def balance_sheet_report(request):
    as_on_date = request.GET.get('as_on_date', str(date.today()))

    asset_accounts = Account.objects.filter(
        account_type='asset', is_active=True
    ).order_by('code')
    liability_accounts = Account.objects.filter(
        account_type='liability', is_active=True
    ).order_by('code')
    equity_accounts = Account.objects.filter(
        account_type='equity', is_active=True
    ).order_by('code')

    def get_balance_to_date(account, as_on):
        lines = JournalLine.objects.filter(
            account=account,
            entry__entry_date__lte=as_on,
            entry__status='posted',
        )
        debits = lines.aggregate(total=Coalesce(Sum('debit'), Value(0), output_field=DecimalField()))['total']
        credits = lines.aggregate(total=Coalesce(Sum('credit'), Value(0), output_field=DecimalField()))['total']
        if account.account_type == 'asset':
            return account.opening_balance + debits - credits
        return account.opening_balance + credits - debits

    asset_data = []
    total_assets = 0
    for acc in asset_accounts:
        bal = get_balance_to_date(acc, as_on_date)
        if acc.code != '1205':
            asset_data.append({'account': acc, 'balance': bal})
            total_assets += bal

    liability_data = []
    total_liabilities = 0
    for acc in liability_accounts:
        bal = get_balance_to_date(acc, as_on_date)
        liability_data.append({'account': acc, 'balance': bal})
        total_liabilities += bal

    equity_data = []
    total_equity = 0
    for acc in equity_accounts:
        bal = get_balance_to_date(acc, as_on_date)
        equity_data.append({'account': acc, 'balance': bal})
        total_equity += bal

    context = {
        'asset_data': asset_data,
        'liability_data': liability_data,
        'equity_data': equity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'as_on_date': as_on_date,
        'title': 'الميزانية العمومية',
    }
    return render(request, 'accounting/balance_sheet.html', context)


@login_required
@permission_required('accounting.view_account', raise_exception=True)
def sales_dashboard(request):
    date_from = request.GET.get('date_from', str(date.today().replace(day=1)))
    date_to = request.GET.get('date_to', str(date.today()))

    orders = Order.objects.filter(
        order_date__date__gte=date_from,
        order_date__date__lte=date_to,
    ).exclude(status='cancelled')

    pos_sales = POSSale.objects.filter(
        sale_date__date__gte=date_from,
        sale_date__date__lte=date_to,
        status='completed',
    )

    order_total = orders.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']
    order_count = orders.count()
    pos_total = pos_sales.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']
    pos_count = pos_sales.count()

    cogs = InventoryValuation.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).aggregate(
        total=Coalesce(Sum('total_cost'), Value(0), output_field=DecimalField())
    )['total']

    context = {
        'order_total': order_total,
        'order_count': order_count,
        'pos_total': pos_total,
        'pos_count': pos_count,
        'grand_total': order_total + pos_total,
        'cogs': cogs,
        'gross_profit': (order_total + pos_total) - cogs,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'تقرير المبيعات',
    }
    return render(request, 'accounting/sales_dashboard.html', context)
