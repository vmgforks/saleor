# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pytest
from django import forms
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from mock import Mock

from saleor.dashboard.product.forms import (ProductClassForm,
                                            ProductClassSelectorForm,
                                            ProductForm)
from saleor.product.models import (Product, ProductAttribute, ProductClass,
                                   ProductVariant)


@pytest.mark.integration
@pytest.mark.django_db
def test_stock_record_update_works(admin_client, product_in_stock):
    variant = product_in_stock.variants.get()
    stock = variant.stock.order_by('-quantity_allocated').first()
    quantity = stock.quantity
    quantity_allocated = stock.quantity_allocated
    url = reverse(
        'dashboard:variant-stock-update', kwargs={
            'product_pk': product_in_stock.pk,
            'variant_pk': variant.pk,
            'stock_pk': stock.pk})
    admin_client.post(url, {
        'variant': stock.variant_id, 'location': stock.location.id,
        'cost_price': stock.cost_price.net,
        'quantity': quantity + 5})
    new_stock = variant.stock.get(pk=stock.pk)
    assert new_stock.quantity == quantity + 5
    assert new_stock.quantity_allocated == quantity_allocated


def test_valid_product_class_form(color_attribute, size_attribute):
    data = {'name': "Testing Class",
            'product_attributes': [color_attribute.pk],
            'variant_attributes': [size_attribute.pk],
            'has_variants': True}
    form = ProductClassForm(data)
    assert form.is_valid()

    # Don't allow same attribute in both fields
    data['variant_attributes'] = [color_attribute.pk, size_attribute.pk]
    data['product_attributes'] = [size_attribute.pk]
    form = ProductClassForm(data)
    assert not form.is_valid()


def test_variantless_product_class_form(color_attribute, size_attribute):
    data = {'name': "Testing Class",
            'product_attributes': [color_attribute.pk],
            'variant_attributes': [],
            'has_variants': False}
    form = ProductClassForm(data)
    assert form.is_valid()

    # Don't allow variant attributes when no variants
    data = {'name': "Testing Class",
            'product_attributes': [color_attribute.pk],
            'variant_attributes': [size_attribute.pk],
            'has_variants': False}
    form = ProductClassForm(data)
    assert not form.is_valid()


def test_edit_used_product_class(db):
    product_class = ProductClass.objects.create(name='New class',
                                                has_variants=True)
    product = Product.objects.create(
        name='Test product', price=10, product_class=product_class)
    ProductVariant.objects.create(product=product, sku='1234')

    # When all products have only one variant you can change
    # has_variants to false
    assert product.variants.all().count() == 1
    data = {'name': product_class.name,
            'product_attributes': product_class.product_attributes.all(),
            'variant_attributes': product_class.variant_attributes.all(),
            'has_variants': False}
    form = ProductClassForm(data, instance=product_class)
    assert form.is_valid()

    data = {'name': product_class.name,
            'product_attributes': product_class.product_attributes.all(),
            'variant_attributes': product_class.variant_attributes.all(),
            'has_variants': True}
    form = ProductClassForm(data, instance=product_class)
    assert form.is_valid()

    # Test has_variants validator which prevents turning off when product
    # has multiple variants
    ProductVariant.objects.create(product=product, sku='12345')
    assert product.variants.all().count() == 2
    data = {'name': product_class.name,
            'product_attributes': product_class.product_attributes.all(),
            'variant_attributes': product_class.variant_attributes.all(),
            'has_variants': False}
    form = ProductClassForm(data, instance=product_class)
    assert not form.is_valid()
    assert 'has_variants' in form.errors.keys()


def test_change_attributes_in_product_form(db, product_in_stock,
                                           color_attribute):
    product = product_in_stock
    product_class = product.product_class
    text_attribute = ProductAttribute.objects.create(slug='author',
                                                     name='Author')
    product_class.product_attributes.add(text_attribute)
    color_value = color_attribute.values.first()
    new_author = 'Main Tester'
    new_color = color_value.pk
    data = {'name': product.name,
            'price': product.price.gross,
            'categories': [c.pk for c in product.categories.all()],
            'description': 'description',
            'attribute-author': new_author,
            'attribute-color': new_color}
    form = ProductForm(data, instance=product)
    assert form.is_valid()
    product = form.save()
    assert product.get_attribute(color_attribute.pk) == smart_text(new_color)
    assert product.get_attribute(text_attribute.pk) == new_author


def test_get_formfield_name_with_unicode_characters(db):
    text_attribute = ProductAttribute.objects.create(slug=u'ąęαβδηθλμπ',
                                                     name=u'ąęαβδηθλμπ')
    assert text_attribute.get_formfield_name() == 'attribute-ąęαβδηθλμπ'


def test_view_product_toggle_publish(db, admin_client, product_in_stock):
    product = product_in_stock
    url = reverse('dashboard:product-publish', kwargs={'pk': product.pk})
    response = admin_client.post(url)
    assert response.status_code == 200
    data = {'success': True, 'is_published': False}
    assert json.loads(response.content.decode('utf8')) == data
    admin_client.post(url)
    product.refresh_from_db()
    assert product.is_published
