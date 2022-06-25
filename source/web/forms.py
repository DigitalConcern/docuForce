from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import Accordion, AccordionGroup
from django import forms
from django.forms import TextInput, Textarea, ChoiceField, Select, CheckboxInput
from django.shortcuts import render

from . import models
from crispy_forms.layout import Field, Layout



class ProgramForm(forms.ModelForm):
    {}


