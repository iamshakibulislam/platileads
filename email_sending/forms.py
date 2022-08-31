from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget

class messageForm(forms.Form):
    message0 = forms.CharField(widget=CKEditorWidget())

    


def getFollowupForm(formno):
    class followupForm(forms.Form):
        #formno = None
        def __init__(self,*args,**kwargs):
        
            
            super().__init__(*args,**kwargs)

            self.fields[formno] = forms.CharField(widget=CKEditorWidget(config_name='followup'),label=False)

        
        #formno = forms.CharField(widget=CKEditorWidget(config_name='followup'))
        
        
    
    return followupForm()
    

