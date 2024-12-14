# views.py

from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponse
from .models import Etudiant, CarteEtudiant, Enseignant, UniteDEnseignement, Semestre, Matier, Niveau, Note
from .forms import EtudiantForm, CarteEtudiantForm, EnseignantForm, UniteDEnseignementForm, SemestreForm, MatierForm, NiveauForm, NoteForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.http import JsonResponse


from django.http import HttpResponseForbidden
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime 
from datetime import date
from django.db.models import Count
from django.shortcuts import render
from django.http import FileResponse
from .models import Etudiant
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum

# def custom_logout(request):
#     logout(request)
#     return redirect('login')
def home(request):
    # Nombre d'étudiants inscrits
    nombre_etudiants = Etudiant.objects.count()

    # Nombre d'enseignants inscrits
    nombre_enseignants = Enseignant.objects.count()

    # Nombre d'étudiants inscrits par niveau
    l1_count = Etudiant.objects.filter(niveau__nom='L1').count()
    l2_count = Etudiant.objects.filter(niveau__nom='L2').count()
    l3_count = Etudiant.objects.filter(niveau__nom='L3').count()
    m1_count = Etudiant.objects.filter(niveau__nom='M1').count()
    m2_count = Etudiant.objects.filter(niveau__nom='M2').count()

    # Passer les statistiques au template
    return render(request, 'home.html', {
        'l1_count': l1_count,
        'l2_count': l2_count,
        'l3_count': l3_count,
        'm1_count': m1_count,
        'm2_count': m2_count,
    })



def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après l'inscription
            return redirect('login')  # Redirection après l'inscription
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Vues pour les étudiants
def liste_etudiants(request):
    etudiants = Etudiant.objects.all()  # Or your logic to fetch students
    for etudiant in etudiants:
        today = date.today()
        age = today.year - etudiant.date_naissance.year - ((today.month, today.day) < (etudiant.date_naissance.month, etudiant.date_naissance.day))
        etudiant.age = age  # This assumes you have an 'age' field in the model (optional)
    context = {'etudiants': etudiants}
    return render(request, 'liste.html', context)



def detail_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    return render(request, 'detail.html', {'etudiant': etudiant})

def ajouter_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                etudiant = form.save()
                messages.success(request, "Étudiant ajouté avec succès!")
                return redirect('liste_etudiants')
            except IntegrityError:
                messages.error(request, "Un étudiant avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'formulaire.html', {'form': form})
    else:
        form = EtudiantForm()
    return render(request, 'formulaire.html', {'form': form})


# def ajouter_etudiant(request):
#     success_message = None
#     form = EtudiantForm()

#     if request.method == 'POST':
#         form = EtudiantForm(request.POST, request.FILES)
#         if form.is_valid():
#             etudiant = form.save()
#             print("Etudiant saved with ID:", etudiant.id)
#             messages.success(request, 'Ajout avec succès.')
#             return redirect('liste_etudiants')
#         else:
#             messages.error(request, 'Corrigez les champs.')
#             print("Form is not valid. Errors:", form.errors)

#     # ... (autres données de contexte)

#     return render(request, 'list.html', {
#         'form': form,
#         'success_message': success_message  # Ajoutez la variable de succès à la contexte
#     })

def modifier_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant modifié avec succès!")
            return redirect('liste_etudiants')
    else:
        form = EtudiantForm(instance=etudiant)
    return render(request, 'formulaire.html', {'form': form})

def supprimer_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        etudiant.delete()
        return redirect('liste_etudiants')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'confirmation.html')


# Vues pour la carte étudiant
# def ajouter_carte(request, etudiant_id):
#     etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
#     universite = Universite.objects.first()  # Utilisation d'une université par défaut
#     if request.method == 'POST':
#         form = CarteEtudiantForm(request.POST, instance=etudiant)
#         if form.is_valid():
#             carte = form.save(commit=False)
#             carte.universite = universite
#             carte.save()
#             messages.success(request, "Carte étudiant générée avec succès!")
#             return redirect('liste_etudiants')
#     else:
#         form = CarteEtudiantForm()
#     return render(request, 'carte/formulaire.html', {'form': form, 'etudiant': etudiant})

####################################################################################################################

def list_enseignant(request):
    enseignants = Enseignant.objects.all() 
    for enseignant in enseignants:
        today = date.today()
        age = today.year - enseignant.date_naissance.year - ((today.month, today.day) < (enseignant.date_naissance.month, enseignant.date_naissance.day))
        enseignant.age = age  
    context = {'enseignants': enseignants}
    return render(request, 'enseignant/list_enseignant.html', context)

def ajouter_enseignant(request):
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                enseignant = form.save()
                messages.success(request, "Énseignant ajouté avec succès!")
                return redirect('list_enseignant')
            except IntegrityError:
                messages.error(request, "Un énseignant avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'enseignant/ajout_enseignant.html', {'form': form})
    else:
        form = EnseignantForm()
    return render(request, 'enseignant/ajout_enseignant.html', {'form': form})

def detail_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    return render(request, 'enseignant/detail_enseignant.html', {'enseignant': enseignant})



def modifier_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES, instance=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, "Enseignant modifié avec succès!")
            return redirect('list_enseignant')
    else:
        form = EnseignantForm(instance=enseignant)
    return render(request, 'enseignant/ajout_enseignant.html', {'form': form})

def supprimer_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        enseignant.delete()
        return redirect('list_enseignant')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'enseignant/confirmation.html')

#######################################################################################################################


def list_ue(request):
    unitedenseignements = UniteDEnseignement.objects.all()   
    context = {'unitedenseignements': unitedenseignements}
    return render(request, 'UE/list_ue.html', context)

def ajouter_ue(request):
    if request.method == 'POST':
        form = UniteDEnseignementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                unitenseignement = form.save()
                messages.success(request, "UniteDEnseignement ajouté avec succès!")
                return redirect('list_ue')
            except IntegrityError:
                messages.error(request, "Un UniteDEnseignement avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'UE/ajout_ue.html', {'form': form})
    else:
        form = UniteDEnseignementForm()
    return render(request, 'UE/ajout_ue.html', {'form': form})




def modifier_ue(request, pk):
    unitedenseignement = get_object_or_404(UniteDEnseignement, pk=pk)
    if request.method == 'POST':
        form = UniteDEnseignementForm(request.POST, request.FILES, instance=unitedenseignement)
        if form.is_valid():
            form.save()
            messages.success(request, "UniteDEnseignement modifié avec succès!")
            return redirect('list_ue')
    else:
        form = UniteDEnseignementForm(instance=unitedenseignement)
    return render(request, 'UE/ajout_ue.html', {'form': form})

def supprimer_ue(request, pk):
    unitedenseignement = get_object_or_404(UniteDEnseignement, pk=pk)
    if request.method == 'POST':
        unitedenseignement.delete()
        return redirect('list_ue')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'UE/confirmation.html')
####################################################################################################################

# def list_cart(request):
#     carteetudiants = CarteEtudiant.objects.all()   
#     context = {'carteetudiants': carteetudiants}
#     return render(request, 'carte/list_cart.html', context)

def ajouter_cart(request):
    if request.method == 'POST':
        form = CarteEtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                carteetudiant = form.save()
                messages.success(request, "CarteEtudiant ajouté avec succès!")
                return redirect('list_cart')
            except IntegrityError:
                messages.error(request, "Un CarteEtudiant avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'carte/ajouter_cart.html', {'form': form})
    else:
        form = UniteDEnseignementForm()
    return render(request, 'carte/ajouter_cart.html', {'form': form})




def modifier_cart(request, pk):
    carteetudiant = get_object_or_404(CarteEtudiant, pk=pk)
    if request.method == 'POST':
        form = CarteEtudiantForm(request.POST, request.FILES, instance=carteetudiant)
        if form.is_valid():
            form.save()
            messages.success(request, "CarteEtudiant modifié avec succès!")
            return redirect('list_cart')
    else:
        form = CarteEtudiantForm(instance=carteetudiant)
    return render(request, 'carte/ajout_cart.html', {'form': form})

def supprimer_cart(request, pk):
    carteetudiant = get_object_or_404(CarteEtudiant, pk=pk)
    if request.method == 'POST':
        carteetudiant.delete()
        return redirect('list_cart')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'carte/confirmation.html')
#########################################################################################################################

def list_semestre(request):
    semestres = Semestre.objects.all().annotate(total_credits=Sum('ue__credits'))
    context = {'semestres': semestres}
    return render(request, 'semestre/list_semestre.html', context)

def ajouter_semestre(request):
    if request.method == 'POST':
        form = SemestreForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                semestre = form.save()
                messages.success(request, "semestre ajouté avec succès!")
                return redirect('list_semestre')
            except IntegrityError:
                messages.error(request, "Un semestre avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'semestre/ajouter_semestre.html', {'form': form})
    else:
        form = SemestreForm()
    return render(request, 'semestre/ajouter_semestre.html', {'form': form})




def modifier_semestre(request, pk):
    semestre = get_object_or_404(Semestre, pk=pk)
    if request.method == 'POST':
        form = SemestreForm(request.POST, request.FILES, instance=semestre)
        if form.is_valid():
            form.save()
            messages.success(request, "semestre modifié avec succès!")
            return redirect('list_semestre')
    else:
        form = SemestreForm(instance=semestre)
    return render(request, 'semestre/ajouter_semestre.html', {'form': form})

def supprimer_semestre(request, pk):
    semestre = get_object_or_404(Semestre, pk=pk)
    if request.method == 'POST':
        semestre.delete()
        return redirect('list_semestre')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'semestre/confirmation.html')
####################################################################################################################

def list_matier(request):
    matiers = Matier.objects.all()   
    context = {'matiers': matiers}
    return render(request, 'matier/list_matier.html', context)

def ajouter_matier(request):
    if request.method == 'POST':
        form = MatierForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                matier = form.save()
                messages.success(request, "matier ajouté avec succès!")
                return redirect('list_matier')
            except IntegrityError:
                messages.error(request, "Un matier avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'matier/ajouter_matier.html', {'form': form})
    else:
        form = MatierForm()
    return render(request, 'matier/ajouter_matier.html', {'form': form})




def modifier_matier(request, pk):
    matier = get_object_or_404(Matier, pk=pk)
    if request.method == 'POST':
        form = MatierForm(request.POST, request.FILES, instance=matier)
        if form.is_valid():
            form.save()
            messages.success(request, "matier modifié avec succès!")
            return redirect('list_matier')
    else:
        form = MatierForm(instance=matier)
    return render(request, 'matier/ajouter_matier.html', {'form': form})

def supprimer_matier(request, pk):
    matier = get_object_or_404(Matier, pk=pk)
    if request.method == 'POST':
        matier.delete()
        return redirect('list_matier')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'matier/confirmation.html')
############################################################################################################################################################

def list_niveau(request):
    niveaus = Niveau.objects.all()   
    context = {'niveaus': niveaus}
    return render(request, 'niveau/list_niveau.html', context)

def ajouter_niveau(request):
    if request.method == 'POST':
        form = NiveauForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                niveau = form.save()
                messages.success(request, "niveau ajouté avec succès!")
                return redirect('list_niveau')
            except IntegrityError:
                messages.error(request, "Un niveau avec ce nom existe déjà.")
            except Exception as e:
                messages.error(request, "Une erreur inconnue s'est produite.")
        return render(request, 'niveau/ajouter_niveau.html', {'form': form})
    else:
        form = NiveauForm()
    return render(request, 'niveau/ajouter_niveau.html', {'form': form})




def modifier_niveau(request, pk):
    niveau = get_object_or_404(Niveau, pk=pk)
    if request.method == 'POST':
        form = NiveauForm(request.POST, request.FILES, instance=niveau)
        if form.is_valid():
            form.save()
            messages.success(request, "niveau modifié avec succès!")
            return redirect('list_niveau')
    else:
        form = NiveauForm(instance=niveau)
    return render(request, 'niveau/ajouter_niveau.html', {'form': form})

def supprimer_niveau(request, pk):
    niveau = get_object_or_404(Niveau, pk=pk)
    if request.method == 'POST':
        niveau.delete()
        return redirect('list_niveau')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'niveau/confirmation.html')
############################################################################################################



def list_note(request):
    notes = Note.objects.all()   
    context = {'notes': notes}
    return render(request, 'note/list_note.html', context)

# def ajouter_note(request):
#     if request.method == 'POST':
#         form = NoteForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 note = form.save()
#                 messages.success(request, "note ajouté avec succès!")
#                 return redirect('list_note')
#             except IntegrityError:
#                 messages.error(request, "Un note avec ce nom existe déjà.")
#             except Exception as e:
#                 messages.error(request, "Une erreur inconnue s'est produite.")
#         return render(request, 'note/ajouter_note.html', {'form': form})
#     else:
#         form = NoteForm()
#     return render(request, 'note/ajouter_note.html', {'form': form})

def ajouter_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_note')
    else:
        form = NoteForm()
    return render(request, 'note/ajouter_note.html', {'form': form})

def get_ue(request, semestre_id):
    ues = UniteDEnseignement.objects.filter(semestre__id=semestre_id).values('id', 'nom')
    return JsonResponse({'ues': list(ues)})

def get_matiere(request, ue_id):
    matieres = Matier.objects.filter(unitedenseignement__id=ue_id).values('id', 'nom')
    return JsonResponse({'matieres': list(matieres)})

def etudiant_det(request, pk):
    etudiant = Etudiant.objects.get(pk=pk)
    notes = Note.objects.filter(etudiant=etudiant)
    ues = UniteDEnseignement.objects.all()
    for ue in ues:
        ue.a_obtenu_credits = a_obtenu_tous_les_credits_ue(etudiant, ue)
    return render(request, 'note/etudiant_detail.html', {'etudiant': etudiant, 'notes': notes, 'ues': ues})

            
    



def modifier_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "note modifié avec succès!")
            return redirect('list_note')
    else:
        form = NoteForm(instance=note)
    return render(request, 'note/ajouter_note.html', {'form': form})

def supprimer_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        return redirect('list_note')  # Replace with the URL of your student list view
    # You can consider adding a confirmation view here
    return render(request, 'note/confirmation.html')




# def generate_pdf(request, pk):
#     etudiant = Etudiant.objects.get(pk=pk)

#     # Créer un buffer en mémoire pour stocker le PDF
#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     # Définir les styles
#     styles = getSampleStyleSheet()
#     styleN = styles["Normal"]

#     # Ajouter du contenu au PDF
#     pdf.drawString(50, 750, "Carte d'Étudiant")
#     pdf.setFont("Helvetica-Bold", 16)
#     pdf.drawString(50, 700, f"Nom Complet: {etudiant.nom_complet}")
#     pdf.setFont("Helvetica", 12)
#     pdf.drawString(50, 680, f"Niveau: {etudiant.niveau}")
#     # ... ajouter les autres champs de la même manière ...

#     # Ajouter une image (si une photo est disponible)
#     if etudiant.photo:
#         img = Image(etudiant.photo.path, width=100, height=100)
#         img.wrap(width=100, height=100)
#         img.hAlign = 'CENTER'
#         pdf.drawImage(img, 300, 650)

#     # Créer un paragraphe avec un texte plus long (exemple)
#     ptext = f"Cette carte est valable jusqu'au 31/12/2024."
#     pdf.drawString(50, 50, ptext)

#     pdf.save()

#     # Retourner le PDF en tant que réponse HTTP
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename='carte_etudiant.pdf')





###############################################################################################



# def generate_card_pdf(request, pk):
#     etudiant = Etudiant.objects.get(pk=pk)

#     # Créer un buffer en mémoire pour stocker le PDF
#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     # Ajouter du contenu au PDF (à personnaliser selon vos besoins)
#     pdf.drawString(100, 750, f"Carte d'Étudiant")
#     pdf.drawString(100, 700, f"Nom: {etudiant.nom}")
#     pdf.drawString(100, 650, f"Prénom: {etudiant.prenom}")
#     # ... ajouter d'autres informations

#     # Ajouter une image (si une photo est disponible)
#     if etudiant.photo:
#         pdf.drawImage(etudiant.photo.path, 150, 500, width=100, height=100)

#     pdf.save()
#     buffer.seek(0)

#     return FileResponse(buffer, as_attachment=True, filename='carte_etudiant.pdf')

# def list_cart(request, pk):
#     etudiant = Etudiant.objects.get(pk=pk)
#     return render(request, 'carte/list_cart.html', {'etudiant': etudiant})




# def generer_carte_etudiant(request, etudiant_id):
#     etudiant = get_object_or_404(Etudiant, pk=etudiant_id)

#     # Créer une nouvelle entrée dans CarteEtudiant
#     carte = CarteEtudiant(etudiant=etudiant)
#     carte.save()

#     # Générer le PDF
#     pdf = canvas.Canvas(f"cartes_etudiants/{carte.id}.pdf")

#     # ... (le reste du code de génération du PDF comme dans l'exemple précédent)

#     pdf.showPage()
#     pdf.save()

#     messages.success(request, "Carte d'étudiant générée avec succès.")
#     return redirect('liste_etudiants')  # Rediriger vers la liste des étudiants




# def generer_carte_etudiant(request, etudiant_id):

#     etudiant = get_object_or_404(Etudiant, pk=etudiant_id)

#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=(148.5 * mm, 105 * mm))  # A4 size in millimeters

#     # Ministry Information (assuming it's at the top)
#     pdf.setFont("Helvetica", 9)
#     pdf.drawString(10 * mm, 95 * mm, "MINISTERE DE L'ENSEIGNEMENT SUPERIEUR")
#     pdf.drawString(10 * mm, 92 * mm, "ET DE LA RECHERCHE SCIENTIFIQUE")

#     # University Logo (assuming it's on the top left corner)
#     # Replace 'logo.jpg' with the actual path to your logo image
#     pdf.drawImage("static/logo.png", 10 * mm, 85 * mm, width=30 * mm, height=20 * mm)
  

#     # University Name (assuming it's centered below the logo)
#     pdf.setFont("Helvetica-Bold", 12)
#     pdf.drawCentredString(74.25 * mm, 80 * mm, "UNIVERSITE DE FIANARANTSOA")

#     # Institution Name (assuming it's centered below the university name)
#     pdf.setFont("Helvetica-Bold", 10)
#     pdf.drawCentredString(74.25 * mm, 75 * mm, "Ecole Nationale d'Informatique")

#     # Title (assuming it's centered below the institution name)
#     pdf.setFont("Helvetica-Bold", 14)
#     pdf.drawCentredString(74.25 * mm, 68 * mm, "Carte d'Étudiant")

#     # Student Photo (assuming it's on the right side)
#     if etudiant.photo:
#         pdf.drawImage(etudiant.photo.path, 110 * mm, 70 * mm, width=35 * mm, height=40 * mm)

#     # Information section (assuming it's on the left side)
#     pdf.setFont("Helvetica-Bold", 9)
#     pdf.drawString(10 * mm, 62 * mm, "Nom:")
#     pdf.drawString(10 * mm, 58 * mm, "Prénom:")
#     pdf.drawString(10 * mm, 54 * mm, "N° d'Immatriculation:")
#     pdf.drawString(10 * mm, 50 * mm, "Date de Naissance:")
#     pdf.drawString(10 * mm, 46 * mm, "Lieu de Naissance:")
#     pdf.drawString(10 * mm, 42 * mm, "Téléphone:")
#     pdf.drawString(10 * mm, 38 * mm, "Sexe:")
#     pdf.drawString(10 * mm, 34 * mm, "Centre de Formation:")
#     pdf.drawString(10 * mm, 30 * mm, "Parcours:")
#     pdf.drawString(10 * mm, 26 * mm, "Niveau:")

#     # Fill student data
#     pdf.setFont("Helvetica", 8)
#     pdf.drawString(30 * mm, 62 * mm, f"{etudiant.nom}")
#     pdf.drawString(30 * mm, 58 * mm, f"{etudiant.prenom}")
#     pdf.drawString(30 * mm, 54 * mm, f"{etudiant.immatriculation}")
#     pdf.drawString(50 * mm, 50 * mm, f"{etudiant.date_naissance.strftime('%d/%m/%Y')}")
#     pdf.drawString(50 * mm, 46 * mm, f"{etudiant.lieu}")
#     pdf.drawString(30 * mm, 42 * mm, f"{etudiant.num_telephone}")
#     pdf.drawString(22 * mm, 38 * mm, f"{etudiant.get_sexe_display()}")  # Adjust text position to 
#     pdf.drawString(200, 340, f"{etudiant.get_centre_formation_display()}")  # Assuming right-aligned

#     # Adjust positions based on your design
#     pdf.drawString(50, 300, f"{etudiant.get_parcours_display()}")  # Assuming left-aligned at Y=300mm
#     pdf.drawString(100, 260, f"{etudiant.niveau}")  # Assuming left-aligned at Y=260mm

#     # ... Add other student data

#     if etudiant.photo:
#         pdf.drawImage(etudiant.photo.path, 400, 600, width=100, height=120)
        


#     pdf.save() 

#     buffer.seek(0) 

#     return FileResponse(buffer, as_attachment=True, filename='carte_etudiant.pdf') 


def generer_carte_etudiant(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    
    # Récupérer le niveau de l'étudiant
    niveau_etudiant = etudiant.niveau
    
    # Récupérer le niveau suivant si possible
    niveau_suivant = Niveau.get_next_niveau(niveau_etudiant)
    
    return render(request, 'carte/carte_etudiant.html', {
        'etudiant': etudiant,
        'niveau_suivant': niveau_suivant
    })



def afficher_carte_etudiant(request, etudiant_id):
    response = generer_carte_etudiant(request, etudiant_id)

    if response.status_code == 200:
        # Extract the PDF content
        pdf_content = response.content

        # Render the PDF in the template
        return render(request, 'carte/afficher_carte.html', {'pdf_content': pdf_content})
    else:
        # Handle errors
        return render(request, 'erreur.html', {'error_message': 'Erreur lors de la génération de la carte'})
    
    