############################################
# Siril Script voor Seestar Fotometrie
# Workflow: Master-Flat -> Green-channel Extraction -> Stacking
############################################

requires 1.2.0

# 1. Voorbereiden Flats
cd flats
convert flat_ -out=../process
cd ../process
# Stack flats zonder normalisatie voor puurheid
stack flat_ rej 3 3 -nonorm -out=master-flat

# 2. Voorbereiden Lights
cd ../lights
convert light_ -out=../process
cd ../process

# 3. Kalibratie met Master-Flat
# We gebruiken -cfa om de Bayer-matrix intact te laten voor extractie
calibrate light_ -flat=master-flat -cfa

# 4. Extractie van de Groene kanalen (G1 + G2)
# Voor fotometrie gebruiken we 'extract', dit halveert de resolutie 
# maar behoudt de pure ADU-waarden zonder interpolatie-fouten.
extract pp_light_ -green

# 5. Registratie (Alignment)
# Global star alignment op de groene frames
register g_pp_light_

# 6. Stacking
# We stacken de geregistreerde groene frames
stack r_g_pp_light_ rej 3 3 -norm=none -out=photometry_final_G
