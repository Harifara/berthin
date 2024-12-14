# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Etudiant, CarteEtudiant, Enseignant, UniteDEnseignement, Semestre, Matier, Niveau, Note
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # Assurez-vous que ce modèle existe
        fields = ['email', 'first_name', 'last_name']  # Ajoutez les champs nécessaires

class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['immatriculation', 'nom', 'prenom', 'date_naissance','sexe', 'num_telephone', 'lieu', 'centre_formation', 'parcours', 'niveau', 'photo']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'date_naissance': {
                'invalid': "Veuillez entrer une date de naissance valide.",
            },
        }


# class CarteEtudiantForm(forms.ModelForm):
#     class Meta:
#         model = CarteEtudiant
#         fields = ['etudiant']  # Formulaire pour associer la carte à l'étudiant


class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ['nom', 'prenom','sexe', 'num_telephone', 'photo', 'date_naissance', 'email']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'date_naissance': {
                'invalid': "Veuillez entrer une date de naissance valide.",
            },
        }


class CarteEtudiantForm(forms.ModelForm):
    class Meta:
        model = CarteEtudiant
        fields = ['etudiant']

class UniteDEnseignementForm(forms.ModelForm):
    class Meta:
        model = UniteDEnseignement
        fields = ['nom', 'credits', 'matiere']  # Include 'matiere' if it's a ManyToManyField

    matiere = forms.ModelMultipleChoiceField(queryset=Matier.objects.all())  # Example for ManyToManyField
        


        
class SemestreForm(forms.ModelForm):
    class Meta:
        model = Semestre
        fields = ['semestre', 'datesemestre', 'ue']
        widgets = {
            'datesemestre': forms.DateInput(attrs={'type': 'date'}),
        }
    
class MatierForm(forms.ModelForm):
    class Meta:
        model = Matier
        fields = ['code', 'nom','enseignant']
        
class NiveauForm(forms.ModelForm):
    class Meta:
        model = Niveau
        fields = ['nom', 'dnom', 'niveau_ordre']  # Liste des champs à inclure dans le formulaire

    def clean_niveau_ordre(self):
        niveau_ordre = self.cleaned_data.get('niveau_ordre')
        if niveau_ordre < 1 or niveau_ordre > 5:  # Validation si le niveau_ordre doit être entre 1 et 5
            raise forms.ValidationError('Le niveau_ordre doit être entre 1 et 5.')
        
        # Vérifier si un niveau avec le même niveau_ordre existe déjà
        if Niveau.objects.filter(niveau_ordre=niveau_ordre).exists():
            raise forms.ValidationError('Un niveau avec ce niveau_ordre existe déjà.')
        
        return niveau_ordre


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['valeur', 'etudiant', 'semestre', 'ue', 'matiere']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ue'].queryset = UniteDEnseignement.objects.none()
        self.fields['matiere'].queryset = Matier.objects.none()

        if 'semestre' in self.data:
            try:
                semestre_id = int(self.data.get('semestre'))
                self.fields['ue'].queryset = UniteDEnseignement.objects.filter(semestre=semestre_id)
            except (ValueError, TypeError):
                pass

        if 'ue' in self.data:
            try:
                ue_id = int(self.data.get('ue'))
                self.fields['matiere'].queryset = Matier.objects.filter(unitedenseignement=ue_id)
            except (ValueError, TypeError):
                pass

        if self.instance.pk:
            if self.instance.semestre:
                self.fields['ue'].queryset = UniteDEnseignement.objects.filter(semestre=self.instance.semestre)
            if self.instance.ue:
                self.fields['matiere'].queryset = Matier.objects.filter(unitedenseignement=self.instance.ue)
