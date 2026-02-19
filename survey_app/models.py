import uuid
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email is required")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(email, password, **extra_fields)


# class User(AbstractBaseUser, PermissionsMixin):
#     ROLE_CHOICES = [
#         ("SURVEYOR", "Surveyor"),
#         ("SUPERVISOR", "Supervisor"),
#         ("DIRECTOR", "Director"),
#         ("ZONAL_CHIEF", "Zonal Chief"),
#         ("GNRB", "GNRB Authority"),
#         ("ADMIN", "Admin"),
#     ]

#     ZONE_CHOICES = [
#         ("NORTH", "North"),
#         ("SOUTH", "South"),
#         ("EAST", "East"),
#         ("WEST", "West"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     mobile = models.CharField(max_length=15)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     zone = models.CharField(max_length=20, choices=ZONE_CHOICES, null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     objects = UserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["name"]

#     def __str__(self):
#         return self.email

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("SURVEYOR", "Surveyor"),
        ("SUPERVISOR", "Supervisor"),
        ("DIRECTOR", "Director"),
        ("ZONAL_CHIEF", "Zonal Chief"),
        ("GNRB", "GNRB Authority"),
        ("ADMIN", "Admin"),
    ]

    ZONE_CHOICES = [
        ("NORTH", "North"),
        ("SOUTH", "South"),
        ("EAST", "East"),
        ("WEST", "West"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # keep username for login
    username = models.CharField(max_length=150,unique=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return f"{self.username} ({self.role})"



# ------------------------
# STATE MODEL
# ------------------------

class State(models.Model):
    name = models.CharField(max_length=150, unique=True)

    # Latitude & Longitude added
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("state", "name")

    def __str__(self):
        return self.name

class SubDistrict(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="subdistricts")
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("district", "name")

    def __str__(self):
        return self.name
class Town(models.Model):
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.CASCADE, related_name="towns")
    base_name = models.CharField(max_length=150)
    sequence = models.IntegerField(default=1)

    class Meta:
        unique_together = ("subdistrict", "base_name", "sequence")

    def save(self, *args, **kwargs):
        if not self.pk:
            count = Town.objects.filter(
                subdistrict=self.subdistrict,
                base_name=self.base_name
            ).count()
            self.sequence = count + 1
        super().save(*args, **kwargs)

    @property
    def name(self):
        if self.sequence > 1:
            return f"{self.base_name} {self.sequence}"
        return self.base_name

    def __str__(self):
        return self.name



# --------------------
# Survey Master
# --------------------

class Survey(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("SUPERVISOR_APPROVED", "Supervisor Approved"),
        ("DIRECTOR_APPROVED", "Director Approved"),
        ("ZONAL_CHIEF_APPROVED", "Zonal Chief Approved"),
        ("GNRB_APPROVED", "GNRB Approved"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    station = models.ForeignKey(Town, on_delete=models.CASCADE)

    surveyor = models.ForeignKey(User, on_delete=models.CASCADE)

    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.station.name} - {self.status}"

STATION_CHOICES = [
    ("CHITTOOR", "CHITTOOR"),
    ("THATITHAPU", "THATITHAPU"),
    ("PELLAKUR", "PELLAKUR"),
    ("TSUNDUPALLE", "TSUNDUPALLE"),
    ("CHILLAKUR", "CHILLAKUR"),
    ("GUMMAGATTA", "GUMMAGATTA"),
    ("KALUVOYA", "KALUVOYA"),
    ("ATLUR", "ATLUR"),
    ("GARLADINNE", "GARLADINNE"),
    ("KODUR", "KODUR"),
    ("VIDAPANAKAL", "VIDAPANAKAL"),
    ("VALETIVARIPALEM", "VALETIVARIPALEM"),
    ("RUDRAVARAM", "RUDRAVARAM"),
    ("PATTIKONDA", "PATTIKONDA"),
    ("ADONI", "ADONI"),
    ("VELDHURTHY", "VELDHURTHY"),
    ("MANGALAGIRI", "MANGALAGIRI"),
    ("SANATHNAGAR", "SANATHNAGAR"),
    ("THULLUR", "THULLUR"),
    ("KROSUR", "KROSUR"),
    ("GOLLAPUDI", "GOLLAPUDI"),
    ("KOYYALAGUDEM", "KOYYALAGUDEM"),
    ("PETTUGOLLAPALLE", "PETTUGOLLAPALLE"),
    ("ADDATEEGALA", "ADDATEEGALA"),
    ("MAREDUMILLI", "MAREDUMILLI"),
    ("GANGAVARAM", "GANGAVARAM"),
    ("MVPCOLONY", "MVPCOLONY"),
    ("VISHAKHAPATTANAM", "VISHAKHAPATTANAM"),
    ("CHINTAPALLI", "CHINTAPALLI"),
    ("SRIKAKULAM", "SRIKAKULAM"),
    ("PARVATIPURAM", "PARVATIPURAM"),
    ("PANGCHAO", "PANGCHAO"),
    ("VIJOYNAGAR", "VIJOYNAGAR"),
    ("NAMPONG", "NAMPONG"),
    ("LADAHQ", "LADAHQ"),
    ("CHAYANGTAJO", "CHAYANGTAJO"),
    ("PASIGHAT", "PASIGHAT"),
    ("LONGDING KOLING HQ", "LONGDING KOLING HQ"),
    ("CHAGLAGAM", "CHAGLAGAM"),
    ("LIMEKINGH.Q", "LIMEKINGH.Q"),
    ("KARGONG", "KARGONG"),
    ("PIDI", "PIDI"),
    ("ANINI", "ANINI"),
    ("SINGA", "SINGA"),
    ("KARIMGANJ", "KARIMGANJ"),
    ("JALUKBARI", "JALUKBARI"),
    ("GOALPARA", "GOALPARA"),
    ("PANIKHAITI", "PANIKHAITI"),
    ("KHANABARIANIANI", "KHANABARIANIANI"),
    ("BARGAON", "BARGAON"),
    ("BARKHOPA", "BARKHOPA"),
    ("UDHIYAGURI", "UDHIYAGURI"),
    ("BISWANATHCIRCLE", "BISWANATHCIRCLE"),
    ("JORHAT", "JORHAT"),
    ("DEMOW", "DEMOW"),
    ("TETARIYAKHURD", "TETARIYAKHURD"),
    ("CHAKAI", "CHAKAI"),
    ("RAFIGANJ", "RAFIGANJ"),
    ("BHAGALPUR", "BHAGALPUR"),
    ("AHMADABAD", "AHMADABAD"),
    ("RAWAICH", "RAWAICH"),
    ("AZAMNAGAR", "AZAMNAGAR"),
    ("MARUUFGANJ", "MARUUFGANJ"),
    ("ROUN", "ROUN"),
    ("DIGHA", "DIGHA"),
    ("MANORI", "MANORI"),
    ("KUKRAUN", "KUKRAUN"),
    ("CHHITWARAKAPUR", "CHHITWARAKAPUR"),
    ("BAISI", "BAISI"),
    ("LAHERIASARAI", "LAHERIASARAI"),
    ("KURSAKATTA", "KURSAKATTA"),
    ("ASHOGI", "ASHOGI"),
    ("PURBIKARGAHIA", "PURBIKARGAHIA"),
    ("SONBARSA", "SONBARSA"),
    ("NAURANGIA", "NAURANGIA"),
    ("MADHYAMARG", "MADHYAMARG"),
    ("KIRANDUL", "KIRANDUL"),
    ("METAPAL", "METAPAL"),
    ("UTLA", "UTLA"),
    ("BENIDHARAUR", "BENIDHARAUR"),
    ("ROTAD", "ROTAD"),
    ("VISHRAMPURI", "VISHRAMPURI"),
    ("ANTAGARH", "ANTAGARH"),
    ("BHANUPRATAPPUR", "BHANUPRATAPPUR"),
    ("NAGRI", "NAGRI"),
    ("KHADGAON", "KHADGAON"),
    ("PIPARCHHEDI", "PIPARCHHEDI"),
    ("ATALNAGAR-NAVA", "ATALNAGAR-NAVA"),
    ("PITHORA", "PITHORA"),
    ("BIRGOAN", "BIRGOAN"),
    ("KHAIRAHA", "KHAIRAHA"),
    ("GUNARBAD", "GUNARBAD"),
    ("DABHARA", "DABHARA"),
    ("KHADI", "KHADI"),
    ("NAWAGARH", "NAWAGARH"),
    ("BALODA", "BALODA"),
    ("PALI", "PALI"),
    ("SHAHPUR", "SHAHPUR"),
    ("KORBI", "KORBI"),
    ("JHIRMITI", "JHIRMITI"),
    ("KELHARI", "KELHARI"),
    ("SINDHOR", "SINDHOR"),
    ("RAMANUJGANJ", "RAMANUJGANJ"),
    ("FUDAM", "FUDAM"),
    ("DELHI_1", "DELHI_1"),
    ("DELHI_2", "DELHI_2"),
    ("DELHI_3", "DELHI_3"),
    ("DELHI_4", "DELHI_4"),
    ("VASCODAGAMA", "VASCODAGAMA"),
    ("OLDGOA", "OLDGOA"),
    ("CALANGUTE", "CALANGUTE"),
    ("VERAVAL", "VERAVAL"),
    ("RAJULA", "RAJULA"),
    ("JUNAGADH", "JUNAGADH"),
    ("JESHAR", "JESHAR"),
    ("JASDAN", "JASDAN"),
    ("KAVANT", "KAVANT"),
    ("BERAJA", "BERAJA"),
    ("DWARKA", "DWARKA"),
    ("RAJKOT_1", "RAJKOT_1"),
    ("RAJKOT_2", "RAJKOT_2"),
    ("KHAMBHAT", "KHAMBHAT"),
    ("JODIYA", "JODIYA"),
    ("VEKARIYA", "VEKARIYA"),
    ("MUNDRA", "MUNDRA"),
    ("MALIA", "MALIA"),
    ("NAKHATRANA", "NAKHATRANA"),
    ("MEGHRAJ", "MEGHRAJ"),
    ("SAMI", "SAMI"),
    ("SANTALPUR", "SANTALPUR"),
    ("SATLASANA", "SATLASANA"),
    ("BHABHAR", "BHABHAR"),
    ("DHANERA", "DHANERA"),
    ("MAVSARI", "MAVSARI"),
    ("FARIDABAD", "FARIDABAD"),
    ("GURUGRAM_1", "GURUGRAM_1"),
    ("GURUGRAM_2", "GURUGRAM_2"),
    ("CHARKHIDADRI", "CHARKHIDADRI"),
    ("ISHARWAL", "ISHARWAL"),
    ("MADINA", "MADINA"),
    ("BHATTUMANDI", "BHATTUMANDI"),
    ("NARWANA", "NARWANA"),
    ("KARNAL_1", "KARNAL_1"),
    ("KARNAL_2", "KARNAL_2"),
    ("PEHOWA", "PEHOWA"),
    ("PANCHKULA", "PANCHKULA"),
    ("SHIMLA_1", "SHIMLA_1"),
    ("SHIMLA_2", "SHIMLA_2"),
    ("SHIMLA_3", "SHIMLA_3"),
    ("SOONA", "SOONA"),
    ("RECKONGPEO", "RECKONGPEO"),
    ("PUNASPA", "PUNASPA"),
    ("HAMIRPUR", "HAMIRPUR"),
    ("BANJAR", "BANJAR"),
    ("UPMOHALDANMOCHHE", "UPMOHALDANMOCHHE"),
    ("NAKO", "NAKO"),
    ("BARSHAINI", "BARSHAINI"),
    ("TABO", "TABO"),
    ("KAZA", "KAZA"),
    ("DAMPHUG", "DAMPHUG"),
    ("HANSA", "HANSA"),
    ("CHOBIA", "CHOBIA"),
    ("KEYLONG", "KEYLONG"),
    ("KUKUMSERI", "KUKUMSERI"),
    ("PARGHWAL", "PARGHWAL"),
    ("SUCHETGARH", "SUCHETGARH"),
    ("JAMMU", "JAMMU"),
    ("GULABGARH", "GULABGARH"),
    ("RAJOURI", "RAJOURI"),
    ("URI", "URI"),
    ("SRINAGAR", "SRINAGAR"),
    ("SISAI", "SISAI"),
    ("DUMRI", "DUMRI"),
    ("RANCHI_1", "RANCHI_1"),
    ("RANCHI_2", "RANCHI_2"),
    ("BISHUNPUR", "BISHUNPUR"),
    ("RANCHI_3", "RANCHI_3"),
    ("RANCHI_4", "RANCHI_4"),
    ("KHALARI", "KHALARI"),
    ("MAJHAULI", "MAJHAULI"),
    ("PAKURIA", "PAKURIA"),
    ("SATGAWAN", "SATGAWAN"),
    ("GUNDLUPETE", "GUNDLUPETE"),
    ("RAMAPURA", "RAMAPURA"),
    ("MAHADESHWARABETTA", "MAHADESHWARABETTA"),
    ("MYSURU_1", "MYSURU_1"),
    ("MYSURU_2", "MYSURU_2"),
    ("RAJAPURA", "RAJAPURA"),
    ("HEBBAL", "HEBBAL"),
    ("ARAKALAGUD", "ARAKALAGUD"),
    ("KONAPPANAAGRAHARA", "KONAPPANAAGRAHARA"),
    ("BENGALURU_1", "BENGALURU_1"),
    ("MANGALURU_1", "MANGALURU_1"),
    ("MANGALURU_2", "MANGALURU_2"),
    ("MANGALURU_3", "MANGALURU_3"),
    ("BENGALURU_2", "BENGALURU_2"),
    ("MANGALURU_4", "MANGALURU_4"),
    ("BENGALURU_3", "BENGALURU_3"),
    ("BENGALURU_4", "BENGALURU_4"),
    ("BEDISWASTE", "BEDISWASTE"),
    ("GADENAHALLI", "GADENAHALLI"),
    ("KALASA", "KALASA"),
    ("TUMAKURU_1", "TUMAKURU_1"),
    ("TUMAKURU_2", "TUMAKURU_2"),
    ("TUMAKURU_3", "TUMAKURU_3"),
    ("CHINTAMANI", "CHINTAMANI"),
    ("NARASIMHARAJAPURA", "NARASIMHARAJAPURA"),
    ("SIRA", "SIRA"),
    ("HOSADURGA", "HOSADURGA"),
    ("SHIVAMOGGA_1", "SHIVAMOGGA_1"),
    ("SHIVAMOGGA_2", "SHIVAMOGGA_2"),
    ("SHIVAMOGGA_3", "SHIVAMOGGA_3"),
    ("SAGARA", "SAGARA"),
    ("DAVANAGERE", "DAVANAGERE"),
    ("HAVERI", "HAVERI"),
    ("MUNDGOD", "MUNDGOD"),
    ("HUVINAHADAGALI", "HUVINAHADAGALI"),
    ("JOIDA", "JOIDA"),
    ("HUBBALLI_1", "HUBBALLI_1"),
    ("KURUGODU", "KURUGODU"),
    ("HUBBALLI_2", "HUBBALLI_2"),
    ("HUBBALLI_3", "HUBBALLI_3"),
    ("KANAKAGIRI", "KANAKAGIRI"),
    ("BELAGAVI_1", "BELAGAVI_1"),
    ("BELAGAVI_2", "BELAGAVI_2"),
    ("BELAGAVI_3", "BELAGAVI_3"),
    ("MANVI", "MANVI"),
    ("BAGALKOT", "BAGALKOT"),
    ("CHIKODI", "CHIKODI"),
    ("BASAVANABAGEWADI", "BASAVANABAGEWADI"),
    ("SHAHAPUR", "SHAHAPUR"),
    ("ALMEL", "ALMEL"),
    ("CHINCHOLI", "CHINCHOLI"),
    ("ALAND", "ALAND"),
    ("POONTHURA", "POONTHURA"),
    ("PALLICHAL", "PALLICHAL"),
    ("MENAMKULAM", "MENAMKULAM"),
    ("ULIYAZHATHURA", "ULIYAZHATHURA"),
    ("ERAMALLOOR", "ERAMALLOOR"),
    ("MUVATTUPUZHA", "MUVATTUPUZHA"),
    ("VYPIN", "VYPIN"),
    ("ALUVA", "ALUVA"),
    ("THRISSUR", "THRISSUR"),
    ("PALAKKAD", "PALAKKAD"),
    ("KYASAPURA", "KYASAPURA"),
    ("NYOMA_1", "NYOMA_1"),
    ("TETHA", "TETHA"),
    ("KHULDO", "KHULDO"),
    ("NYOMA_2", "NYOMA_2"),
    ("CHUSHUL", "CHUSHUL"),
    ("MAN", "MAN"),
    ("ZULIDOK", "ZULIDOK"),
    ("SASPUL", "SASPUL"),
    ("TSATI", "TSATI"),
    ("TERCHEY", "TERCHEY"),
    ("TURTUK", "TURTUK"),
    ("CHANGLUNG", "CHANGLUNG"),
    ("KALPENI", "KALPENI"),
    ("KILTAN", "KILTAN"),
    ("BITRA", "BITRA"),
    ("CHETLAT", "CHETLAT"),
    ("KHAKNARKALAN", "KHAKNARKALAN"),
    ("ATHNER", "ATHNER"),
    ("GONAGHAT", "GONAGHAT"),
    ("SEGAON", "SEGAON"),
    ("BHIKANGAON", "BHIKANGAON"),
    ("CHIMANKHAPA", "CHIMANKHAPA"),
    ("DAHI", "DAHI"),
    ("PUNASA", "PUNASA"),
    ("AMARWARA", "AMARWARA"),
    ("KHIRSADI", "KHIRSADI"),
    ("BAGH", "BAGH"),
    ("SEONIMALWA", "SEONIMALWA"),
    ("KATTIWADAKHAS", "KATTIWADAKHAS"),
    ("ATARIYA_x000D_ATARIYA", "ATARIYA_x000D_ATARIYA"),
    ("INDORE_1", "INDORE_1"),
    ("INDORE_2", "INDORE_2"),
    ("INDORE_3", "INDORE_3"),
    ("GADARWARA", "GADARWARA"),
    ("DINDORI", "DINDORI"),
    ("KHEDA", "KHEDA"),
    ("JABALPUR_1", "JABALPUR_1"),
    ("BHOPAL_1", "BHOPAL_1"),
    ("UJJAIN_1", "UJJAIN_1"),
    ("UJJAIN_2", "UJJAIN_2"),
    ("JABALPUR_2", "JABALPUR_2"),
    ("BHOPAL_2", "BHOPAL_2"),
    ("BHOPAL_3", "BHOPAL_3"),
    ("SHAHDOL", "SHAHDOL"),
    ("KALAPIPAL", "KALAPIPAL"),
    ("PACHORE", "PACHORE"),
    ("DAMOH", "DAMOH"),
    ("SAGARNAGAR", "SAGARNAGAR"),
    ("SAGAR", "SAGAR"),
    ("PANTHPIPALIA", "PANTHPIPALIA"),
    ("TURKI_1", "TURKI_1"),
    ("MANGARAI", "MANGARAI"),
    ("MALTHON", "MALTHON"),
    ("PATNATAMOLI", "PATNATAMOLI"),
    ("SIDHI", "SIDHI"),
    ("DIGHWAR", "DIGHWAR"),
    ("ASHOKNAGAR", "ASHOKNAGAR"),
    ("SATNA", "SATNA"),
    ("MAUGANJ", "MAUGANJ"),
    ("SIRMAUR", "SIRMAUR"),
    ("TURKI_2", "TURKI_2"),
    ("NOWGAON", "NOWGAON"),
    ("MAGARDEH", "MAGARDEH"),
    ("BHITARWAR", "BHITARWAR"),
    ("KHOJIPURA", "KHOJIPURA"),
    ("SEONDHA", "SEONDHA"),
    ("GWALIOR_1", "GWALIOR_1"),
    ("GWALIOR_2", "GWALIOR_2"),
    ("MORENA", "MORENA"),
    ("DEVGAD", "DEVGAD"),
    ("SHIRALA", "SHIRALA"),
    ("RATNAGIRI", "RATNAGIRI"),
    ("MAYANI", "MAYANI"),
    ("SOLAPUR_1", "SOLAPUR_1"),
    ("SOLAPUR_2", "SOLAPUR_2"),
    ("SOLAPUR_3", "SOLAPUR_3"),
    ("PARANDA", "PARANDA"),
    ("MURUD", "MURUD"),
    ("KONDHWA", "KONDHWA"),
    ("KARVENAGAR", "KARVENAGAR"),
    ("PUNE_1", "PUNE_1"),
    ("PUNE_2", "PUNE_2"),
    ("PUNE_3", "PUNE_3"),
    ("PIMPRICHINCHWAD", "PIMPRICHINCHWAD"),
    ("SHELARWADI", "SHELARWADI"),
    ("AHMADPUR", "AHMADPUR"),
    ("KOPRA", "KOPRA"),
    ("APOLLOBANDARCOLABA", "APOLLOBANDARCOLABA"),
    ("NAVIMUMBAI", "NAVIMUMBAI"),
    ("PANVEL", "PANVEL"),
    ("MUMBAI_1", "MUMBAI_1"),
    ("TURBHE", "TURBHE"),
    ("TALOJA", "TALOJA"),
    ("MUMBAI_2", "MUMBAI_2"),
    ("MUMBAI_3", "MUMBAI_3"),
    ("MUMBAI_4", "MUMBAI_4"),
    ("THANE_1", "THANE_1"),
    ("MUMBAI_5", "MUMBAI_5"),
    ("DAMRANCHA", "DAMRANCHA"),
    ("THANE_2", "THANE_2"),
    ("PATHRI", "PATHRI"),
    ("THANE_3", "THANE_3"),
    ("KALYAN", "KALYAN"),
    ("NAIGAON", "NAIGAON"),
    ("NASHIK_1", "NASHIK_1"),
    ("KOLTHAN", "KOLTHAN"),
    ("NASHIK_2", "NASHIK_2"),
    ("JATWADA", "JATWADA"),
    ("NASHIK_3", "NASHIK_3"),
    ("ARNI", "ARNI"),
    ("MEHKAR", "MEHKAR"),
    ("SINDEWAHI", "SINDEWAHI"),
    ("NANDGAON", "NANDGAON"),
    ("YAVATMAL", "YAVATMAL"),
    ("GHATNANDRA", "GHATNANDRA"),
    ("HINGANGHAT", "HINGANGHAT"),
    ("DATTAPURDHAMANGAON", "DATTAPURDHAMANGAON"),
    ("MALKAPUR", "MALKAPUR"),
    ("AMRAVATI", "AMRAVATI"),
    ("NAGPUR_1", "NAGPUR_1"),
    ("KAMPTEE", "KAMPTEE"),
    ("NAGPUR_2", "NAGPUR_2"),
    ("AMGAONKH.", "AMGAONKH."),
    ("WARLA", "WARLA"),
    ("NARKHED", "NARKHED"),
    ("TOLBUNG", "TOLBUNG"),
    ("NAMBASHIKHULLEN", "NAMBASHIKHULLEN"),
    ("JATRAKONA-II", "JATRAKONA-II"),
    ("UMLŽ?REM", "UMLŽ?REM"),
    ("KHANAPARA", "KHANAPARA"),
    ("ZUNHEBOTO", "ZUNHEBOTO"),
    ("KADAGUDA", "KADAGUDA"),
    ("DIGAPAHANDI", "DIGAPAHANDI"),
    ("CHANDRAPUR", "CHANDRAPUR"),
    ("KHALIKOTE", "KHALIKOTE"),
    ("CHILIKANUAPADA", "CHILIKANUAPADA"),
    ("KOKSARA", "KOKSARA"),
    ("JUNAGARH", "JUNAGARH"),
    ("RAIGHAR", "RAIGHAR"),
    ("BHOGARA", "BHOGARA"),
    ("BOIRGAON", "BOIRGAON"),
    ("BHINGARPUR", "BHINGARPUR"),
    ("BHUASUNI", "BHUASUNI"),
    ("CUTTACK", "CUTTACK"),
    ("NARASINGHPUR", "NARASINGHPUR"),
    ("PURUNAKOT", "PURUNAKOT"),
    ("DEULDUNGURI", "DEULDUNGURI"),
    ("PATNAGARH", "PATNAGARH"),
    ("GARHAPARAJANG", "GARHAPARAJANG"),
    ("DANGAPAL", "DANGAPAL"),
    ("CHHENDIPADA", "CHHENDIPADA"),
    ("ANANDAPURPART", "ANANDAPURPART"),
    ("REAMAL", "REAMAL"),
    ("SAMBALPUR", "SAMBALPUR"),
    ("AHARAPADA", "AHARAPADA"),
    ("SARGIDIHI", "SARGIDIHI"),
    ("BADHUNIA", "BADHUNIA"),
    ("ROURKELA", "ROURKELA"),
    ("NETTAPAKKAM", "NETTAPAKKAM"),
    ("KUNICHAMPET", "KUNICHAMPET"),
    ("YANAM", "YANAM"),
    ("MOONAK", "MOONAK"),
    ("LEHRI", "LEHRI"),
    ("MALOUT", "MALOUT"),
    ("CHAURA", "CHAURA"),
    ("FAZILKA", "FAZILKA"),
    ("MALERKOTLA", "MALERKOTLA"),
    ("KOTKAPURA", "KOTKAPURA"),
    ("SASNAGAR(MOHALI)_1", "SASNAGAR(MOHALI)_1"),
    ("SASNAGAR(MOHALI)_2", "SASNAGAR(MOHALI)_2"),
    ("FOCALPOINT", "FOCALPOINT"),
    ("INDUSTRIALZONE", "INDUSTRIALZONE"),
    ("FIROZPUR", "FIROZPUR"),
    ("GARHSHANKAR", "GARHSHANKAR"),
    ("CHHOTIBARANDARII", "CHHOTIBARANDARII"),
    ("HUSSAINPUR", "HUSSAINPUR"),
    ("BASTIBAWAKHEL", "BASTIBAWAKHEL"),
    ("SULTANWIND", "SULTANWIND"),
    ("CHHEHARTA", "CHHEHARTA"),
    ("AJNALA", "AJNALA"),
    ("DERABABANANAK", "DERABABANANAK"),
    ("MARARA", "MARARA"),
    ("SAJJANGARH", "SAJJANGARH"),
    ("KOTRI", "KOTRI"),
    ("RISHABHDEO", "RISHABHDEO"),
    ("DHARIAWAD", "DHARIAWAD"),
    ("PIRAWA", "PIRAWA"),
    ("PHALASIYA", "PHALASIYA"),
    ("SARDA DUNGAR GARH", "SARDA DUNGAR GARH"),
    ("ABUROAD", "ABUROAD"),
    ("ASNAWAR", "ASNAWAR"),
    ("SUKHER", "SUKHER"),
    ("KANERA", "KANERA"),
    ("JALBERI", "JALBERI"),
    ("BARAN", "BARAN"),
    ("SHRINATHPURAM", "SHRINATHPURAM"),
    ("KANSUWA", "KANSUWA"),
    ("SUMERPUR", "SUMERPUR"),
    ("GUDHAMALANI", "GUDHAMALANI"),
    ("BAGODA", "BAGODA"),
    ("GANGAPUR", "GANGAPUR"),
    ("RAILWAYSTATIONAREA", "RAILWAYSTATIONAREA"),
    ("MANDALGARH", "MANDALGARH"),
    ("SHAHPURA_1", "SHAHPURA_1"),
    ("SIWANA", "SIWANA"),
    ("RAMA", "RAMA"),
    ("DEI", "DEI"),
    ("MARWARJUNCTION", "MARWARJUNCTION"),
    ("ASIND", "ASIND"),
    ("GADRAROAD", "GADRAROAD"),
    ("BARMER", "BARMER"),
    ("PANCHLA", "PANCHLA"),
    ("KHANDAR", "KHANDAR"),
    ("KALYANPUR", "KALYANPUR"),
    ("MANPURAKHARDA", "MANPURAKHARDA"),
    ("JOGIDASKAGAON", "JOGIDASKAGAON"),
    ("MALPURA", "MALPURA"),
    ("BONLI", "BONLI"),
    ("SINDHIPURA", "SINDHIPURA"),
    ("BEENJOTA", "BEENJOTA"),
    ("HATHIKHERA", "HATHIKHERA"),
    ("SARMATHURA", "SARMATHURA"),
    ("GHOOGHRA", "GHOOGHRA"),
    ("LOONAR", "LOONAR"),
    ("PHAGI", "PHAGI"),
    ("NADOTI", "NADOTI"),
    ("DECHOO", "DECHOO"),
    ("JEEROTA", "JEEROTA"),
    ("ROOPANGARH", "ROOPANGARH"),
    ("KANOI", "KANOI"),
    ("KISHANPURAATLALWAS", "KISHANPURAATLALWAS"),
    ("KUCHERA", "KUCHERA"),
    ("SHAHGARH", "SHAHGARH"),
    ("BHARATPUR", "BHARATPUR"),
    ("GUWARA SOTI", "GUWARA SOTI"),
    ("AAU", "AAU"),
    ("NADBAI", "NADBAI"),
    ("JAYAL", "JAYAL"),
    ("RAJGARH", "RAJGARH"),
    ("DANTARAMGARH", "DANTARAMGARH"),
    ("NAGAUR", "NAGAUR"),
    ("SHAHPURA_2", "SHAHPURA_2"),
    ("DIDWANA", "DIDWANA"),
    ("SHRIMADHOPUR", "SHRIMADHOPUR"),
    ("LONGEWALA", "LONGEWALA"),
    ("SUTHAR MANDI", "SUTHAR MANDI"),
    ("NOKHA", "NOKHA"),
    ("KAMAN", "KAMAN"),
    ("NECHHWA", "NECHHWA"),
    ("NAWALGARH", "NAWALGARH"),
    ("MUNDAWAR", "MUNDAWAR"),
    ("KISHANGARH", "KISHANGARH"),
    ("RANJITPURA", "RANJITPURA"),
    ("BIWANDI", "BIWANDI"),
    ("ROOPNAGAR", "ROOPNAGAR"),
    ("SURAJGARH", "SURAJGARH"),
    ("SOMASAR", "SOMASAR"),
    ("LUNKARANSAR", "LUNKARANSAR"),
    ("RANISAR", "RANISAR"),
    ("RAWLAMANDI", "RAWLAMANDI"),
    ("NOHAR", "NOHAR"),
    ("ANUPGARH", "ANUPGARH"),
    ("SURATGARH", "SURATGARH"),
    ("UMEWALA", "UMEWALA"),
    ("SRIGANGANAGAR", "SRIGANGANAGAR"),
    ("NAMCHI", "NAMCHI"),
    ("RESHI", "RESHI"),
    ("DENTAM", "DENTAM"),
    ("YANGYANG", "YANGYANG"),
    ("KUPUP", "KUPUP"),
    ("LACHEN", "LACHEN"),
    ("THANGU VALLEY", "THANGU VALLEY"),
    ("THOOTHUKUDI_1", "THOOTHUKUDI_1"),
    ("THOOTHUKUDI_2", "THOOTHUKUDI_2"),
    ("THIRUPARANKUNDRAM", "THIRUPARANKUNDRAM"),
    ("MADURAI_1", "MADURAI_1"),
    ("MADURAI_2", "MADURAI_2"),
    ("MADURAI_3", "MADURAI_3"),
    ("DINDIGUL_1", "DINDIGUL_1"),
    ("DINDIGUL_2", "DINDIGUL_2"),
    ("DINDIGUL_3", "DINDIGUL_3"),
    ("TIRUCHIRAPPALLI_1", "TIRUCHIRAPPALLI_1"),
    ("THANJAVUR_1", "THANJAVUR_1"),
    ("THANJAVUR_2", "THANJAVUR_2"),
    ("THANJAVUR_3", "THANJAVUR_3"),
    ("THIRUVERUMBUR", "THIRUVERUMBUR"),
    ("TIRUCHIRAPPALLI_2", "TIRUCHIRAPPALLI_2"),
    ("PODANUR", "PODANUR"),
    ("COIMBATORE_1", "COIMBATORE_1"),
    ("COIMBATORE_2", "COIMBATORE_2"),
    ("ARULPURAM", "ARULPURAM"),
    ("COIMBATORE_3", "COIMBATORE_3"),
    ("TIRUPPUR_1", "TIRUPPUR_1"),
    ("TIRUPPUR_2", "TIRUPPUR_2"),
    ("TIRUPPUR_3", "TIRUPPUR_3"),
    ("ERODE_1", "ERODE_1"),
    ("ERODE_2", "ERODE_2"),
    ("PALLIPALAYAM", "PALLIPALAYAM"),
    ("SALEM_1", "SALEM_1"),
    ("SALEM_2", "SALEM_2"),
    ("SALEM_3", "SALEM_3"),
    ("VELLORE_1", "VELLORE_1"),
    ("VELLORE_2", "VELLORE_2"),
    ("KARAPAKKAM", "KARAPAKKAM"),
    ("VELLORE_3", "VELLORE_3"),
    ("TAMBARAM", "TAMBARAM"),
    ("VELLORE_4", "VELLORE_4"),
    ("ANNANUR", "ANNANUR"),
    ("VALLUR", "VALLUR"),
    ("AIZA", "AIZA"),
    ("YERRUPALEM", "YERRUPALEM"),
    ("GARIDEPALLI", "GARIDEPALLI"),
    ("KURMALGUDA", "KURMALGUDA"),
    ("RAJENDRANAGARMANDAL", "RAJENDRANAGARMANDAL"),
    ("HAYATNAGAR_1", "HAYATNAGAR_1"),
    ("MARIPEDA", "MARIPEDA"),
    ("GUMMADIVALLI", "GUMMADIVALLI"),
    ("HYDERABAD_1", "HYDERABAD_1"),
    ("SECUNDERABAD_1", "SECUNDERABAD_1"),
    ("HYDERABAD_2", "HYDERABAD_2"),
    ("KAREPALLI", "KAREPALLI"),
    ("SECUNDERABAD_2", "SECUNDERABAD_2"),
    ("ZAHIRABAD", "ZAHIRABAD"),
    ("KOTHAGUDA", "KOTHAGUDA"),
    ("KHAZIPET", "KHAZIPET"),
    ("WARANGAL", "WARANGAL"),
    ("HANUMAKONDA_1", "HANUMAKONDA_1"),
    ("HANUMAKONDA_2", "HANUMAKONDA_2"),
    ("KANGTI", "KANGTI"),
    ("KARIMNAGAR_1", "KARIMNAGAR_1"),
    ("KARIMNAGAR_2", "KARIMNAGAR_2"),
    ("MANTHANI", "MANTHANI"),
    ("KAMMARPALLI", "KAMMARPALLI"),
    ("DANDEPALLI", "DANDEPALLI"),
    ("LINGAPUR", "LINGAPUR"),
    ("SIRIKONDA", "SIRIKONDA"),
    ("KAILASHAHAR", "KAILASHAHAR"),
    ("RAJAPUR", "RAJAPUR"),
    ("VARANASI_1", "VARANASI_1"),
    ("MUGHALSARAI", "MUGHALSARAI"),
    ("VARANASI_2", "VARANASI_2"),
    ("SADWAKALAN", "SADWAKALAN"),
    ("VARANASI_3", "VARANASI_3"),
    ("CHEDIBEER", "CHEDIBEER"),
    ("PRAYAGRAJ", "PRAYAGRAJ"),
    ("NAGRA", "NAGRA"),
    ("KABIRNAGAR", "KABIRNAGAR"),
    ("JHANSI", "JHANSI"),
    ("OLDKATRA", "OLDKATRA"),
    ("BABERU", "BABERU"),
    ("GARSARI", "GARSARI"),
    ("MEHNAGAR", "MEHNAGAR"),
    ("MANIRAMPUR", "MANIRAMPUR"),
    ("PATTI", "PATTI"),
    ("JAMINKAKARGHATTI", "JAMINKAKARGHATTI"),
    ("SHAHGANJ", "SHAHGANJ"),
    ("ATRAULIA", "ATRAULIA"),
    ("MANPUR", "MANPUR"),
    ("RAMPURA", "RAMPURA"),
    ("NAUBASTA", "NAUBASTA"),
    ("JAJMAU", "JAJMAU"),
    ("PANKI", "PANKI"),
    ("CIVILLINES", "CIVILLINES"),
    ("UTELA", "UTELA"),
    ("NAWABGANJ", "NAWABGANJ"),
    ("BARAULIKHALILABAD", "BARAULIKHALILABAD"),
    ("KHALILABAD", "KHALILABAD"),
    ("BAIRIALIPUR", "BAIRIALIPUR"),
    ("LUCKNOW", "LUCKNOW"),
    ("DAULATGANJ", "DAULATGANJ"),
    ("BARABANKI", "BARABANKI"),
    ("MUDIYAR", "MUDIYAR"),
    ("MOYAIYANPUR", "MOYAIYANPUR"),
    ("DOMARIYAGANJ", "DOMARIYAGANJ"),
    ("SURUCHIPURAMCOLONY", "SURUCHIPURAMCOLONY"),
    ("AGRA", "AGRA"),
    ("MAHMUDABAD", "MAHMUDABAD"),
    ("AKBARPURAUNCHHA", "AKBARPURAUNCHHA"),
    ("NAUTANWA", "NAUTANWA"),
    ("GOPALPUR", "GOPALPUR"),
    ("PACHPERWA", "PACHPERWA"),
    ("GOPAMAU", "GOPAMAU"),
    ("BAMHNAWA", "BAMHNAWA"),
    ("SIKANDRARAO", "SIKANDRARAO"),
    ("BHINGA", "BHINGA"),
    ("DHANIPUR", "DHANIPUR"),
    ("DHAURRAMAFI", "DHAURRAMAFI"),
    ("RANJITGARHI", "RANJITGARHI"),
    ("BUDAUN", "BUDAUN"),
    ("NIGOHI", "NIGOHI"),
    ("HARKHAPUR", "HARKHAPUR"),
    ("KHURJA", "KHURJA"),
    ("AONLA", "AONLA"),
    ("BHIRA", "BHIRA"),
    ("PATELBIHARCOLONY", "PATELBIHARCOLONY"),
    ("GREATERNOIDA", "GREATERNOIDA"),
    ("CHANDANCHAUKI", "CHANDANCHAUKI"),
    ("NOIDA", "NOIDA"),
    ("PILIBHIT", "PILIBHIT"),
    ("GHAZIABAD", "GHAZIABAD"),
    ("HASANPUR", "HASANPUR"),
    ("TASHKA", "TASHKA"),
    ("HAYATNAGAR_2", "HAYATNAGAR_2"),
    ("LALIYANA", "LALIYANA"),
    ("BAGPAT", "BAGPAT"),
    ("BIJNOR", "BIJNOR"),
    ("SHAMLI", "SHAMLI"),
    ("SAHARANPUR_1", "SAHARANPUR_1"),
    ("SAHARANPUR_2", "SAHARANPUR_2"),
    ("SAHARANPUR_3", "SAHARANPUR_3"),
    ("JHALAKUDI", "JHALAKUDI"),
    ("BHINGRADRANGE", "BHINGRADRANGE"),
    ("KALAGARH", "KALAGARH"),
    ("NAINIDANDA", "NAINIDANDA"),
    ("DHARCHULA", "DHARCHULA"),
    ("TEEJAM", "TEEJAM"),
    ("BHARARISAIN", "BHARARISAIN"),
    ("KALAPANI", "KALAPANI"),
    ("DEHRADUN_1", "DEHRADUN_1"),
    ("DEHRADUN_2", "DEHRADUN_2"),
    ("KUTI", "KUTI"),
    ("DEHRADUN_3", "DEHRADUN_3"),
    ("DEHRADUN_4", "DEHRADUN_4"),
    ("KEDARNATH", "KEDARNATH"),
    ("BADRINATH", "BADRINATH"),
    ("GANGOTRI", "GANGOTRI"),
    ("BAKKHALI", "BAKKHALI"),
    ("BALIGERIA", "BALIGERIA"),
    ("HALDIA", "HALDIA"),
    ("RAJPURSONARPUR", "RAJPURSONARPUR"),
    ("PURBAPUTIARY", "PURBAPUTIARY"),
    ("PUJALI", "PUJALI"),
    ("MAHESHTALA", "MAHESHTALA"),
    ("KGHODHATI", "KGHODHATI"),
    ("KOLKATA", "KOLKATA"),
    ("RAJARHAT", "RAJARHAT"),
    ("HOWRAH_1", "HOWRAH_1"),
    ("HOWRAH_2", "HOWRAH_2"),
    ("MADHYAMGRAM", "MADHYAMGRAM"),
    ("RAJYADHARPUR", "RAJYADHARPUR"),
    ("BAGHMUNDI", "BAGHMUNDI"),
    ("MAJHDIA", "MAJHDIA"),
    ("BAMUNARA", "BAMUNARA"),
    ("DURGAPUR_1", "DURGAPUR_1"),
    ("DURGAPUR_2", "DURGAPUR_2"),
    ("BETAI", "BETAI"),
    ("KHARIBONA", "KHARIBONA"),
    ("RAGHUNATHGANJ", "RAGHUNATHGANJ"),
    ("KALIACHAK", "KALIACHAK"),
    ("BARTALI", "BARTALI"),
    ("KUMARGANJ", "KUMARGANJ"),
    ("KALIYAGANJ", "KALIYAGANJ"),
    ("ISLAMPUR", "ISLAMPUR"),
    ("HALDIBARI", "HALDIBARI"),
    ("KUMARGRAM", "KUMARGRAM"),
    ("JAIGAON", "JAIGAON"),
    ("SUKHANIBASTI", "SUKHANIBASTI"),
]

# class Survey(models.Model):
#     STATUS_CHOICES = [
#         ("DRAFT", "Draft"),
#         ("SUBMITTED", "Submitted"),
#         ("SUPERVISOR_APPROVED", "Supervisor Approved"),
#         ("DIRECTOR_APPROVED", "Director Approved"),
#         ("ZONAL_CHIEF_APPROVED", "Zonal Chief Approved"),
#         ("GNRB_APPROVED", "GNRB Approved"),
#         ("REJECTED", "Rejected"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     station = models.CharField(max_length=150, choices=STATION_CHOICES)
#     surveyor = models.ForeignKey(User, on_delete=models.CASCADE)
#     # latitude = models.DecimalField(max_digits=9, decimal_places=6)
#     # longitude = models.DecimalField(max_digits=9, decimal_places=6)
#     status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")
#     remarks = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.station

class SurveySubSite(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    survey = models.ForeignKey(
        Survey,
        related_name="subsites",
        on_delete=models.CASCADE
    )

    location = models.CharField(max_length=150)

    priority = models.IntegerField(
        default=1,
        help_text="Priority of subsite (lower number = higher priority)"
    )

    # ✅ OPTIONAL RINEX FILE
    rinex_file = models.FileField(
        upload_to="rinex_files/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        return f"{self.location} (Priority {self.priority})"


class SurveyLocation(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Location for {self.survey.location}"



# class SurveyMonument(models.Model):
#     MONUMENT_TYPE = [("GROUND", "Ground"), ("ROOFTOP", "Rooftop")]

#     survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
#     monument_type = models.CharField(max_length=10, choices=MONUMENT_TYPE)
#     building_stories = models.IntegerField(null=True, blank=True)
#     accessibility = models.TextField()
#     surroundings = models.TextField()
    
#     def  __str__(self):
#         return f"Monument for {self.survey.subsite_name}"


class SurveyMonument(models.Model):

    MONUMENT_TYPE = [
        ("GROUND", "Ground"),
        ("ROOFTOP", "Rooftop"),
    ]

    BUILDING_STORIES = [
        ("SINGLE", "Single Story"),
        ("DOUBLE", "Double Story"),
        ("TRIPLE", "Triple Story"),
    ]

    CHECKBOX_CHOICES = [
        "Site Properly Accessible",
        "Site is clean and free from litter",
        "Site NOT in low-lying areas or flood area",
    ]

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveymonument"
    )

    monument_type = models.CharField(
        max_length=10,
        choices=MONUMENT_TYPE
    )

    # Only required if Rooftop
    building_stories = models.CharField(
        max_length=10,
        choices=BUILDING_STORIES,
        blank=True,
        null=True
    )

    # Checkbox list
    site_conditions = models.JSONField(
        default=list,
        blank=True
    )

    def __str__(self):
        return f"Monument for {self.survey.subsite_name}"


# EMI_SOURCE_CHOICES = [
#     "HT Powerline",
#     "Distribution Powerline",
#     "Transformer",
#     "Mobile Tower",
#     "Other Radio Transmitter",
#     "Electric Grid Station",
#     "Water body",
#     "Glazed window or Surface",
#     "Others",
# ]


# class SurveySkyVisibility(models.Model):
#     survey = models.OneToOneField(
#         "SurveySubSite",
#         on_delete=models.CASCADE,
#         related_name="surveyskyvisibility"
#     )

#     polar_chart_image = models.ImageField(
#         upload_to="sky_visibility/",
#         null=True,
#         blank=True
#     )

#     # List of EMI objects
#     multipath_emi_source = models.JSONField(
#         default=list,
#         blank=True
#     )

#     remarks = models.TextField(blank=True)

#     def __str__(self):
#         return f"Sky Visibility for {self.survey.subsite_name}"

EMI_SOURCE_CHOICES = [
    "HT Powerline",
    "Distribution Powerline",
    "Transformer",
    "Mobile Tower",
    "Other Radio Transmitter",
    "Electric Grid Station",
    "Water body",
    "Glazed window or Surface",
    "Others",
]

DIRECTION_CHOICES = [
    "North",
    "Northeast",
    "East",
    "Southeast",
    "South",
    "Southwest",
    "West",
    "Northwest",
]


class SurveySkyVisibility(models.Model):
    survey = models.OneToOneField(
        "SurveySubSite",
        on_delete=models.CASCADE,
        related_name="surveyskyvisibility"
    )

    polar_chart_image = models.ImageField(
        upload_to="sky_visibility/",
        null=True,
        blank=True
    )

    # Each item example:
    # [
    #   {
    #     "source": "HT Powerline",
    #     "direction": "North",
    #     "approx_distance_m": 200
    #   }
    # ]
    multipath_emi_source = models.JSONField(
        default=list,
        blank=True
    )

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Sky Visibility for {self.survey.location}"



# class SurveyPower(models.Model):
#     survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
#     ac_grid = models.BooleanField()
#     solar_possible = models.BooleanField()
#     sun_hours = models.IntegerField()
    
#     def __str__(self):
#         return f"Power Details for {self.survey.subsite_name}"

class SurveyPower(models.Model):

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveypower"
    )

    ac_grid = models.BooleanField()

    # ✅ NEW FIELD
    ac_grid_distance_meter = models.IntegerField(
        null=True,
        blank=True,
        help_text="Distance of nearest AC power connection in meters"
    )

    solar_possible = models.BooleanField()

    solar_exposure_hours = models.IntegerField()

    def __str__(self):
        return f"Power Details for {self.survey.subsite_name}"



    
PROVIDER_CHOICES = [
    "Airtel",
    "Vodafone Idea",
    "JIO",
    "BSNL",
    "Others",
]


class SurveyConnectivity(models.Model):

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveyconnectivity"
    )

    # Existing
    gsm_4g = models.JSONField(default=list, blank=True)
    broadband = models.JSONField(default=list, blank=True)
    fiber = models.JSONField(default=list, blank=True)

    # ✅ NEW FIELD
    airfiber = models.JSONField(default=list, blank=True)

    # Others free text
    others_gsm_4g = models.CharField(max_length=255, blank=True)
    others_broadband = models.CharField(max_length=255, blank=True)
    others_fiber = models.CharField(max_length=255, blank=True)

    # ✅ NEW OTHERS FIELD
    others_airfiber = models.CharField(max_length=255, blank=True)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Connectivity Details for {self.survey.subsite_name}"


class SurveyPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_site = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    north_photo = models.ImageField(upload_to="survey_photos/" )
    east_photo = models.ImageField(upload_to="survey_photos/" )
    south_photo = models.ImageField(upload_to="survey_photos/" )
    west_photo = models.ImageField(upload_to="survey_photos/")
    captured_at = models.DateTimeField(auto_now_add=True)
    
    def  __str__(self):
        return f"Photos of {self.sub_site.subsite_name}"

class SurveyApproval(models.Model):
    LEVEL_CHOICES = [
        (1, "Supervisor"),
        (2, "Director"),
        (3, "Zonal Chief"),
        (4, "GNRB"),
    ]

    DECISION = [("APPROVED", "Approved"), 
                ("REJECTED", "Rejected")
                ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    approval_level = models.IntegerField(choices=LEVEL_CHOICES)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(max_length=10, choices=DECISION)
    remarks = models.TextField()
    approved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.survey.site_name} - Level {self.approval_level} - {self.decision}"



class RinexFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.FileField(
        upload_to="rinex_files/",
        null=True,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RINEX File {self.id}"
