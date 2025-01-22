from django.contrib import admin
from .models import GroupLink, Link, PriceLink, AnalogLink, AnalogLinkPrice
from import_export import resources


admin.site.register(GroupLink)

class LinkResource(resources.ModelResource):
    class Meta:
        model = Link

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    search_fields = ('name', 'link')
    list_display = ( 'group_link', 'name', 'link',)
    resource_classes = [LinkResource]




@admin.register(PriceLink)
class PriceLinkAdmin(admin.ModelAdmin):
    list_display = ('price', 'data_parser_price', 'price_link', )
    

admin.site.register(AnalogLink)
admin.site.register(AnalogLinkPrice)