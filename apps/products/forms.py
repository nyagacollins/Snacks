from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Product


class ProductPriceForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['price', 'is_available']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('price', css_class='form-group col-md-8 mb-0'),
                Column('is_available', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Price', css_class='btn btn-primary')
        )


class SnackSelectionForm(forms.Form):
    mandazi_quantity = forms.IntegerField(
        min_value=0, 
        max_value=20, 
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    eggs_quantity = forms.IntegerField(
        min_value=0, 
        max_value=10, 
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('mandazi_quantity', css_class='form-group col-md-6 mb-0'),
                Column('eggs_quantity', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Calculate Total', css_class='btn btn-success')
        )