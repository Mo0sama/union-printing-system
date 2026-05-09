from django.core.management.base import BaseCommand

from apps.calculator.models import (
    GiveawayCategory,
    GiveawayPricingTier,
    GiveawayProduct,
    PricingTier,
    ServiceCategory,
    ServiceProduct,
)


class Command(BaseCommand):
    help = 'بذر البيانات الأولية لحاسبة الأسعار (المنتجات والشرائح السعرية)'

    def handle(self, *args, **options):
        self._seed_services()
        self._seed_giveaways()
        self.stdout.write(self.style.SUCCESS('تم بذر بيانات حاسبة الأسعار بنجاح'))

    def _seed_services(self):
        cat_data = [
            {'name': 'Business Cards', 'name_ar': 'بطاقات عمل', 'icon': 'bi-card-heading', 'sort_order': 1},
            {'name': 'Flyers', 'name_ar': 'فلير', 'icon': 'bi-file-earmark-text', 'sort_order': 2},
            {'name': 'Brochures', 'name_ar': 'بروشورات', 'icon': 'bi-journal-text', 'sort_order': 3},
            {'name': 'Banners', 'name_ar': 'بنرات', 'icon': 'bi-images', 'sort_order': 4},
            {'name': 'Posters', 'name_ar': 'بوسترات', 'icon': 'bi-image', 'sort_order': 5},
            {'name': 'Stickers', 'name_ar': 'استيكرات', 'icon': 'bi-sticky', 'sort_order': 6},
            {'name': 'Booklets', 'name_ar': 'كتيبات', 'icon': 'bi-book', 'sort_order': 7},
            {'name': 'Envelopes', 'name_ar': 'أظرف', 'icon': 'bi-envelope', 'sort_order': 8},
        ]
        for cd in cat_data:
            cat, _ = ServiceCategory.objects.get_or_create(name=cd['name'], defaults=cd)
            self._seed_service_products(cat)

    def _seed_service_products(self, category):
        products_map = {
            'Business Cards': [
                {'name': 'Standard Business Cards', 'name_ar': 'بطاقات عمل عادية'},
                {'name': 'Premium Business Cards', 'name_ar': 'بطاقات عمل بريميوم'},
            ],
            'Flyers': [
                {'name': 'A5 Flyer', 'name_ar': 'فلير مقاس A5'},
                {'name': 'A4 Flyer', 'name_ar': 'فلير مقاس A4'},
            ],
            'Brochures': [
                {'name': 'Tri-fold Brochure', 'name_ar': 'بروشور ثلاثي الطي'},
                {'name': 'Bi-fold Brochure', 'name_ar': 'بروشور ثنائي الطي'},
            ],
            'Banners': [
                {'name': 'Roll-up Banner', 'name_ar': 'بانر رول أب'},
                {'name': 'Vinyl Banner', 'name_ar': 'بانر فينيل'},
            ],
            'Posters': [
                {'name': 'A3 Poster', 'name_ar': 'بوستر A3'},
                {'name': 'A2 Poster', 'name_ar': 'بوستر A2'},
            ],
            'Stickers': [
                {'name': 'Standard Sticker', 'name_ar': 'استيكر عادي'},
                {'name': 'Glossy Sticker', 'name_ar': 'استيكر لمّاع'},
            ],
            'Booklets': [
                {'name': 'A5 Booklet', 'name_ar': 'كتيب A5'},
                {'name': 'A4 Booklet', 'name_ar': 'كتيب A4'},
            ],
            'Envelopes': [
                {'name': 'Standard Envelope', 'name_ar': 'ظرف عادي'},
                {'name': 'Window Envelope', 'name_ar': 'ظرف شباك'},
            ],
        }
        prods = products_map.get(category.name, [])
        for pd in prods:
            product, created = ServiceProduct.objects.get_or_create(
                category=category, name=pd['name'], defaults=pd
            )
            if created:
                self._seed_service_tiers(product)

    def _seed_service_tiers(self, product):
        standard_tiers = [
            (100, 500, 5.00),
            (501, 2000, 4.00),
            (2001, 5000, 3.00),
            (5001, 999999, 2.50),
        ]
        for qf, qt, price in standard_tiers:
            PricingTier.objects.get_or_create(
                product=product, qty_from=qf, qty_to=qt,
                defaults={'unit_price': price}
            )

    def _seed_giveaways(self):
        cat_data = [
            {'name': 'Pens', 'name_ar': 'أقلام', 'icon': 'bi-pen', 'sort_order': 1},
            {'name': 'USB Drives', 'name_ar': 'فلاش ميموري', 'icon': 'bi-usb-drive', 'sort_order': 2},
            {'name': 'Notebooks', 'name_ar': 'دفاتر', 'icon': 'bi-journal', 'sort_order': 3},
            {'name': 'Mugs', 'name_ar': 'أكواب', 'icon': 'bi-cup-hot', 'sort_order': 4},
            {'name': 'Bags', 'name_ar': 'شنط', 'icon': 'bi-bag', 'sort_order': 5},
            {'name': 'Keychains', 'name_ar': 'كولكات', 'icon': 'bi-key', 'sort_order': 6},
            {'name': 'Badges', 'name_ar': 'بطاقات تعريف', 'icon': 'bi-person-badge', 'sort_order': 7},
        ]
        for cd in cat_data:
            cat, _ = GiveawayCategory.objects.get_or_create(name=cd['name'], defaults=cd)
            self._seed_giveaway_products(cat)

    def _seed_giveaway_products(self, category):
        products_map = {
            'Pens': [
                {'name': 'Metal Pen', 'name_ar': 'قلم معدني', 'has_options': True},
                {'name': 'Plastic Pen', 'name_ar': 'قلم بلاستيك', 'has_options': True},
            ],
            'USB Drives': [
                {'name': 'USB Flash Drive', 'name_ar': 'فلاش ميموري', 'has_options': True},
            ],
            'Notebooks': [
                {'name': 'A5 Notebook', 'name_ar': 'دفتر A5'},
                {'name': 'A4 Notebook', 'name_ar': 'دفتر A4'},
            ],
            'Mugs': [
                {'name': 'Ceramic Mug', 'name_ar': 'كوب سيراميك'},
                {'name': 'Travel Mug', 'name_ar': 'كوب سفري'},
            ],
            'Bags': [
                {'name': 'Non-woven Bag', 'name_ar': 'شنتة غير منسوجة'},
                {'name': 'Paper Bag', 'name_ar': 'شنتة ورق'},
            ],
            'Keychains': [
                {'name': 'Acrylic Keychain', 'name_ar': 'كولكة أكريليك'},
                {'name': 'Metal Keychain', 'name_ar': 'كولكة معدنية'},
            ],
            'Badges': [
                {'name': 'ID Badge', 'name_ar': 'بطاقة تعريف'},
                {'name': 'Lanyard', 'name_ar': 'حامل بطاقة'},
            ],
        }
        prods = products_map.get(category.name, [])
        for pd in prods:
            product, created = GiveawayProduct.objects.get_or_create(
                category=category, name=pd['name'], defaults=pd
            )
            if created:
                self._seed_giveaway_options(product)
                self._seed_giveaway_tiers(product)

    def _seed_giveaway_options(self, product):
        options_map = {
            'Metal Pen': [
                {'name': 'Blue Ink', 'name_ar': 'حبر أزرق', 'price_adjustment': 0},
                {'name': 'Black Ink', 'name_ar': 'حبر أسود', 'price_adjustment': 0},
                {'name': 'Red Ink', 'name_ar': 'حبر أحمر', 'price_adjustment': 0},
            ],
            'Plastic Pen': [
                {'name': 'Blue Ink', 'name_ar': 'حبر أزرق', 'price_adjustment': 0},
                {'name': 'Black Ink', 'name_ar': 'حبر أسود', 'price_adjustment': 0},
            ],
            'USB Flash Drive': [
                {'name': '8GB', 'name_ar': '8 جيجابايت', 'price_adjustment': 0},
                {'name': '16GB', 'name_ar': '16 جيجابايت', 'price_adjustment': 2},
                {'name': '32GB', 'name_ar': '32 جيجابايت', 'price_adjustment': 5},
            ],
        }
        opts = options_map.get(product.name, [])
        for od in opts:
            GiveawayProduct.objects.get_or_create(
                category=product.category, name=product.name,
                defaults={'has_options': True}
            )
            from apps.calculator.models import GiveawayOption
            GiveawayOption.objects.get_or_create(
                product=product, name=od['name'], defaults=od
            )

    def _seed_giveaway_tiers(self, product):
        standard_tiers = [
            (50, 200, 3.00),
            (201, 500, 2.50),
            (501, 2000, 2.00),
            (2001, 999999, 1.50),
        ]
        for qf, qt, price in standard_tiers:
            GiveawayPricingTier.objects.get_or_create(
                product=product, qty_from=qf, qty_to=qt, option=None,
                defaults={'unit_price': price}
            )
