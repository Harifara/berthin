# models.py

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import FileExtensionValidator
import datetime
from django.utils.translation import gettext as _
from django.db.models import Sum



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    
class Niveau(models.Model):
    # Nom du niveau (par exemple L1, L2, M, M2)
    nom = models.CharField(max_length=10, choices=[
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2')
    ])

    # Description longue du niveau (par exemple "Licence 1", "Master 2")
    dnom = models.CharField(max_length=100)

    # Champ pour stocker l'ordre des niveaux
    niveau_ordre = models.PositiveIntegerField()

    def __str__(self):
        return self.dnom

    class Meta:
        ordering = ['niveau_ordre']  # Cela garantit que les niveaux sont triés par ordre croissant

    @classmethod
    def get_next_niveau(cls, current_niveau):
        """
        Cette méthode renvoie le niveau suivant.
        """
        try:
            return cls.objects.get(niveau_ordre=current_niveau.niveau_ordre + 1)
        except cls.DoesNotExist:
            return None  # Aucun niveau suivant si le maximum est atteint



class Etudiant(models.Model):
    annee_academique = models.IntegerField(default=datetime.date.today().year)
    PARCOURS_CHOICES = [
        ('IG', 'Informatique General'),
        ('GB', 'Génie Logiciel'),
        ('SR', 'Systèmes et réseaux'),
    ]
    CENTRE_CHOICES = [
        ('Toliara', 'Toliara'),
        ('Fianarantsoa', 'Fianarantsoa'),
    ]

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    immatriculation = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    num_telephone = PhoneNumberField(blank=True)
    lieu = models.CharField(max_length=100)
    centre_formation = models.CharField(max_length=50, choices=CENTRE_CHOICES)
    parcours = models.CharField(max_length=50, choices=PARCOURS_CHOICES)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)  # New field for sex
    photo = models.ImageField(upload_to='photos/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])

    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    def calculer_age(self):
        today = date.today()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))

   
def est_admis(self):
        # Vérifier si toutes les unités d'enseignement de l'année scolaire sont validées
        for semestre in Semestre.objects.filter(datesemestre__year=self.annee_academique):
            for ue in semestre.ue.all():
                if not ue.is_valide(self):
                    return False  # L'étudiant n'est pas admis si une UE est invalidée
        return True  # L'étudiant est admis si toutes les UE sont validées

def generer_CarteEtudiant(self):
    # Vérifier les performances et mettre à jour le niveau en cas de réussite
    if self.est_admis():
        # Obtenez le niveau suivant en fonction de l'ordre
        next_niveau = Niveau.get_next_niveau(self.niveau)
        if next_niveau:
            self.niveau = next_niveau
            self.save()
    # Créer un nouvel objet CarteEtudiant avec les informations mises à jour de l'étudiant
    carte = CarteEtudiant.objects.create(etudiant=self)


    


class CarteEtudiant(models.Model):  # New model for student ID cards
    etudiant = models.OneToOneField(Etudiant, on_delete=models.CASCADE)  # Link to student model
    date_generation = models.DateField(auto_now_add=True)  # Date the card is generated

    def __str__(self):
        return f"Carte Etudiant - {self.etudiant.nom} {self.etudiant.prenom}"

class Enseignant(models.Model):
    
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    num_telephone = PhoneNumberField(blank=True)
    email = models.EmailField()
    photo = models.ImageField(upload_to='photos/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Matier(models.Model):
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.nom 
     

class UniteDEnseignement(models.Model):
    nom = models.CharField(max_length=255)
    credits = models.IntegerField()
    matiere = models.ManyToManyField(Matier)

    def __str__(self):
        return self.nom

    def is_valide(self, etudiant):
        total_notes = 0
        nombre_matiere = 0
        for matiere in self.matiere.all():
            note = Note.objects.filter(etudiant=etudiant, matiere=matiere).first()
            if note and note.is_valide():
                total_notes += note.valeur
                nombre_matiere += 1
            else:
                return False  # Si une matière est invalidée par une note 0, l'UE n'est pas valide
        return (total_notes / nombre_matiere) >= 10 if nombre_matiere > 0 else False



class Semestre(models.Model):
    semestre = models.CharField(max_length=20)
    ue = models.ManyToManyField(UniteDEnseignement)
    datesemestre = models.DateField()
    
 

    def get_moyenne_etudiant(self, etudiant):
        notes_semestre = Note.objects.filter(etudiant=etudiant, semestre=self)
        return notes_semestre.aggregate(Avg('valeur'))['valeur__avg']


    def __str__(self):
        return f"Semestre {self.semestre} "
    @classmethod
    def get_total_credits(cls, semestre_instance):  # Use cls instead of self
        return semestre_instance.ue_set.aggregate(total_credits=Sum('credits'))['total_credits']
    


class Note(models.Model):
    valeur = models.IntegerField()
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matier, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    ue = models.ForeignKey(UniteDEnseignement, on_delete=models.CASCADE)

    def __str__(self):
        return f"Note {self.valeur} - {self.etudiant.nom} - {self.matiere.nom} - Semestre {self.semestre.semestre} - {self.ue.nom}"

    def is_valide(self):
        return self.valeur != 0  # Si la note est 0, la matière est invalidée


def a_obtenu_tous_les_credits_ue(etudiant, ue):
    notes_ue = Note.objects.filter(etudiant=etudiant, matiere__in=ue.matiere.all(), semestre=ue.semestre)
    moyenne_ue = notes_ue.aggregate(Avg('valeur'))['valeur__avg']
    nombre_matieres = ue.matiere.count()
    return moyenne_ue >= 10 and notes_ue.count() == nombre_matieres
