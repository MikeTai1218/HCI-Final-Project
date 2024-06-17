from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserForm(UserCreationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter username"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter email-address"}))
    password1 = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Enter password", "type":"password"}))
    password2 = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"confirm password", "type":"password"}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ResumeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop("initial_values", None)
        super(ResumeForm, self).__init__(*args, **kwargs)

        # Set initial values for each field based on the dictionary
        if initial_values:
            self.fields["research_area"].initial = initial_values.get(
                "research_area", ""
            )
            self.fields["education"].initial = initial_values.get("education", "")
            self.fields["key_skills"].initial = initial_values.get("key_skills", "")
            self.fields["work_experiences"].initial = initial_values.get(
                "work_experiences", ""
            )
            self.fields["relevant_coursework"].initial = initial_values.get(
                "relevant_coursework", ""
            )
            self.fields["extracurricular"].initial = initial_values.get(
                "extracurricular", ""
            )
            self.fields["language_skills"].initial = initial_values.get(
                "language_skills", ""
            )

    research_area = forms.CharField(
        label="研究領域",
        max_length=100,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "例: 智慧電梯系統"}
        ),
    )
    education = forms.CharField(
        label="最高學歷",
        max_length=100,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "例: 國立陽明交通大學資訊工程學系"}
        ),
    )
    key_skills = forms.CharField(
        label="專業技能",
        max_length=100,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "例: Python, Java, C++, Django, HTML, CSS, JavaScript, MySQL, Git",
            }
        ),
    )
    work_experiences = forms.CharField(
        label="工作經驗",
        max_length=100,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "例: NYCU 科技有限公司-軟體工程師(2023/7 - 2024/2)",
            }
        ),
    )
    relevant_coursework = forms.CharField(
        label="相關課程",
        max_length=100,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "例: 多媒體與人機互動總整與實作, 資料結構與物件導向, 演算法概論",
            }
        ),
    )
    extracurricular = forms.CharField(
        label="課外活動",
        max_length=100,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "例: 梅竹黑客松"}
        ),
    )
    language_skills = forms.CharField(
        label="外語能力",
        max_length=100,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "例: TOEFL 112(R30 L30 W27 L25)",
            }
        ),
    )

