// UNION FOR DIGITAL PRINTING - Management System JavaScript
$(document).ready(function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    // Format currency inputs
    $('.currency-input').on('input', function() {
        var val = $(this).val().replace(/[^0-9.]/g, '');
        $(this).val(val);
    });

    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm($(this).data('confirm') || 'Are you sure you want to delete this?')) {
            e.preventDefault();
        }
    });

    // Select2-like search in selects
    $('.search-select').on('keyup', function() {
        var filter = $(this).val().toLowerCase();
        $(this).next('select').find('option').each(function() {
            if ($(this).text().toLowerCase().indexOf(filter) > -1) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Calculate totals for inline forms
    $(document).on('input', '.calc-qty, .calc-price, .calc-discount', function() {
        var row = $(this).closest('tr');
        var qty = parseFloat(row.find('.calc-qty').val()) || 0;
        var price = parseFloat(row.find('.calc-price').val()) || 0;
        var discount = parseFloat(row.find('.calc-discount').val()) || 0;
        var total = qty * price * (1 - discount / 100);
        row.find('.calc-total').val(total.toFixed(2));
        updateOrderTotal();
    });

    function updateOrderTotal() {
        var subtotal = 0;
        $('.calc-total').each(function() {
            subtotal += parseFloat($(this).val()) || 0;
        });
        $('#id_subtotal').val(subtotal.toFixed(2));
        var discountType = $('#id_discount_type').val();
        var discountVal = parseFloat($('#id_discount_value').val()) || 0;
        var taxPct = parseFloat($('#id_tax_percentage').val()) || 0;
        var afterDiscount = subtotal;
        if (discountType === 'percentage') {
            afterDiscount = subtotal * (1 - discountVal / 100);
        } else if (discountType === 'fixed') {
            afterDiscount = subtotal - discountVal;
        }
        var taxAmt = afterDiscount * taxPct / 100;
        var shipping = parseFloat($('#id_shipping_cost').val()) || 0;
        var total = afterDiscount + taxAmt + shipping;
        $('#id_tax_amount').val(taxAmt.toFixed(2));
        $('#id_total').val(total.toFixed(2));
        $('#total-display').text(total.toFixed(2));
    }

    $(document).on('change', '#id_discount_type, #id_discount_value, #id_tax_percentage, #id_shipping_cost', function() {
        updateOrderTotal();
    });

    // POS: Add item to cart
    $(document).on('click', '.pos-item-btn', function() {
        var desc = $(this).data('name');
        var price = $(this).data('price');
        addToCart(desc, price);
    });

    function addToCart(desc, price) {
        var existing = $('.pos-cart-item').filter(function() {
            return $(this).data('name') === desc;
        });
        if (existing.length) {
            var qty = parseInt(existing.find('.item-qty').val()) + 1;
            existing.find('.item-qty').val(qty);
            existing.find('.item-total').text((qty * price).toFixed(2));
        } else {
            var html = '<div class="pos-cart-item d-flex align-items-center justify-content-between py-2 border-bottom" data-name="' + desc + '">' +
                '<div><small>' + desc + '</small><br><small class="text-muted">' + price.toFixed(2) + '</small></div>' +
                '<div class="d-flex align-items-center gap-2">' +
                '<input type="number" class="form-control form-control-sm item-qty" style="width:60px" value="1" min="1">' +
                '<span class="item-total fw-bold">' + price.toFixed(2) + '</span>' +
                '<button class="btn btn-sm btn-outline-danger pos-remove-item"><i class="bi bi-x"></i></button>' +
                '</div></div>';
            $('.pos-cart-items').append(html);
        }
        updatePosTotal();
    }

    $(document).on('click', '.pos-remove-item', function() {
        $(this).closest('.pos-cart-item').remove();
        updatePosTotal();
    });

    $(document).on('change', '.item-qty', function() {
        updatePosTotal();
    });

    function updatePosTotal() {
        var total = 0;
        $('.pos-cart-item').each(function() {
            var qty = parseInt($(this).find('.item-qty').val()) || 0;
            var priceText = $(this).find('.text-muted').text() || '0';
            var price = parseFloat(priceText) || 0;
            var lineTotal = qty * price;
            $(this).find('.item-total').text(lineTotal.toFixed(2));
            total += lineTotal;
        });
        $('#pos-total-amount').text(total.toFixed(2));
        $('#pos-total-input').val(total.toFixed(2));
    }

    // Quick search filter for tables
    $('#table-search').on('keyup', function() {
        var val = $(this).val().toLowerCase();
        $('.table-custom tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(val) > -1);
        });
    });

    // Print receipt
    $(document).on('click', '.print-receipt', function() {
        var receiptContent = $(this).data('receipt') || '';
        var w = window.open('', '_blank', 'width=300,height=600');
        w.document.write('<html><head><title>Receipt</title>');
        w.document.write('<style>body{font-family:monospace;padding:20px;font-size:12px;}');
        w.document.write('.text-center{text-align:center;}.border-bottom{border-bottom:1px dashed #000;padding-bottom:10px;margin-bottom:10px;}');
        w.document.write('</style></head><body>');
        w.document.write(receiptContent);
        w.document.write('</body></html>');
        w.document.close();
        w.print();
    });

    // Sidebar active state
    var currentPath = window.location.pathname;
    $('.sidebar .nav-link').each(function() {
        var href = $(this).attr('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            $(this).addClass('active');
        }
        if (currentPath === '/' && href === '/') {
            $(this).addClass('active');
        }
    });

    // Language direction adjustment
    function adjustDirection() {
        var lang = $('html').attr('lang');
        if (lang === 'ar') {
            $('html').attr('dir', 'rtl');
        } else {
            $('html').attr('dir', 'ltr');
        }
    }
    adjustDirection();
});
