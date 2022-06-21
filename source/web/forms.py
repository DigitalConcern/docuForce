from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Accordion, AccordionGroup
from django import forms
from django.forms import TextInput, Textarea, ChoiceField, Select, CheckboxInput
from django.shortcuts import render

from . import models
from crispy_forms.layout import Field, Layout


# class ProgramForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Accordion(
#                 AccordionGroup('First Group',
#                                'radio_buttons'
#                                ),
#                 AccordionGroup('First Group',
#                                'radio_buttons'
#                                ),
#             )
#         )

class ProgramForm(forms.ModelForm):
    class Meta:
        model = models.Programs
        fields = ['name', 'description', 'info', 'faq', 'category', 'is_active', 'link']
        widgets = {
            "name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название программы'}),
            "description": Textarea(attrs={'class': 'form-control', 'style': 'height: 100px', 'placeholder': 'Текст, который отображается в списке программ'}),
            "info": Textarea(attrs={'class': 'form-control', 'style': 'height: 200px', 'placeholder': 'Текст, который пользователь видит при переходе к программе'}),
            "faq": Textarea(attrs={'class': 'form-control', 'style': 'height: 200px', 'placeholder': 'Ответы на часто задаваемые вопросы по программе'}),
            "category": Select(attrs={'class': 'form-select'},
                               choices=(('students', 'Студенты'), ('school', 'Школьники'))),
            "is_active": CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            "link": TextInput(attrs={'class': 'form-control', 'placeholder': 'https://www.croc.ru/'}),

        }


class UserForm(forms.ModelForm):
    class Meta:
        model = models.ActiveUsers
        fields = ['user_id', 'code_name', 'user_name', 'grade', 'is_admin']
        widgets = {
            "user_id": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            "code_name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            "user_name": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            "grade": TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            "is_admin": CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

class FAQForm(forms.ModelForm):
    class Meta:
        model = models.FAQ
        fields = ['text']
        widgets = {
            "text": Textarea(attrs={'class': 'form-control','style': 'height: 300px', 'placeholder': 'ФАК-ю'})
        }