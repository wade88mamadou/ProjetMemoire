-- =====================================================
-- SCRIPT SQL DDL - TABLEAU DE BORD CONFORMITE MEDICALE
-- Conformité RGPD, HIPAA, CDP Sénégal
-- =====================================================

-- Suppression des tables si elles existent (pour le développement)
-- DROP TABLE IF EXISTS DossiersConformiteRegles;
-- DROP TABLE IF EXISTS AccesEtablissements;
-- DROP TABLE IF EXISTS ResultatsAnalyses;
-- DROP TABLE IF EXISTS Analyses;
-- DROP TABLE IF EXISTS Alertes;
-- DROP TABLE IF EXISTS Infections;
-- DROP TABLE IF EXISTS Vaccins;
-- DROP TABLE IF EXISTS Residences;
-- DROP TABLE IF EXISTS Alimentations;
-- DROP TABLE IF EXISTS Comportements;
-- DROP TABLE IF EXISTS Logements;
-- DROP TABLE IF EXISTS Prescriptions;
-- DROP TABLE IF EXISTS ReglesConformite;
-- DROP TABLE IF EXISTS ParametresConformite;
-- DROP TABLE IF EXISTS Rapports;
-- DROP TABLE IF EXISTS DossiersMedicaux;
-- DROP TABLE IF EXISTS Patients;
-- DROP TABLE IF EXISTS Utilisateurs;
-- DROP TABLE IF EXISTS Etablissements;
-- DROP TABLE IF EXISTS Professions;
-- DROP TABLE IF EXISTS TypesLogement;
-- DROP TABLE IF EXISTS RegimesAlimentaires;
-- DROP TABLE IF EXISTS NiveauxEtudes;

-- =====================================================
-- TABLES DE REFERENCE
-- =====================================================

-- Table: Etablissements
CREATE TABLE Etablissements (
    idEtablissement VARCHAR(255) PRIMARY KEY,
    nomEtablissement VARCHAR(255) NOT NULL,
    adresse VARCHAR(500),
    telephone VARCHAR(50),
    email VARCHAR(255),
    dateCreation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Professions
CREATE TABLE Professions (
    idProfession VARCHAR(255) PRIMARY KEY,
    nomProfession VARCHAR(255) NOT NULL,
    description TEXT
);

-- Table: TypesLogement
CREATE TABLE TypesLogement (
    idTypeLogement VARCHAR(255) PRIMARY KEY,
    libelle VARCHAR(255) NOT NULL,
    description TEXT
);

-- Table: RegimesAlimentaires
CREATE TABLE RegimesAlimentaires (
    idRegimeAlimentaire VARCHAR(255) PRIMARY KEY,
    libelle VARCHAR(255) NOT NULL,
    description TEXT
);

-- Table: NiveauxEtudes
CREATE TABLE NiveauxEtudes (
    idNiveauEtude VARCHAR(255) PRIMARY KEY,
    libelle VARCHAR(255) NOT NULL,
    description TEXT
);

-- =====================================================
-- TABLES PRINCIPALES
-- =====================================================

-- Table: Utilisateurs
CREATE TABLE Utilisateurs (
    idUtilisateur VARCHAR(255) PRIMARY KEY,
    dateCreation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    specialite VARCHAR(255),
    motDePasse VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('administrateur', 'medecin', 'user_simple')),
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    estActive BOOLEAN NOT NULL DEFAULT TRUE,
    email VARCHAR(255) UNIQUE,
    telephone VARCHAR(50),
    derniereConnexion DATETIME
);

-- Table: Patients
CREATE TABLE Patients (
    idPatient VARCHAR(255) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    dateNaissance DATE NOT NULL,
    sexe VARCHAR(10) NOT NULL CHECK (sexe IN ('Homme', 'Femme')),
    poids DECIMAL(5,2),
    taille DECIMAL(4,2),
    lieuNaissance VARCHAR(255),
    nationalite VARCHAR(255),
    niveauEtude VARCHAR(255),
    etablissement VARCHAR(255),
    profession VARCHAR(255),
    dateCreation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (niveauEtude) REFERENCES NiveauxEtudes(idNiveauEtude) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (etablissement) REFERENCES Etablissements(idEtablissement) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: DossiersMedicaux
CREATE TABLE DossiersMedicaux (
    idDossier VARCHAR(255) PRIMARY KEY,
    idPatient VARCHAR(255) NOT NULL,
    idUtilisateur VARCHAR(255),
    nomDossier VARCHAR(255) NOT NULL,
    dateCreation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    commentaireGeneral TEXT,
    statut VARCHAR(50) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Archivé', 'Fermé')),
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (idUtilisateur) REFERENCES Utilisateurs(idUtilisateur) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Rapports
CREATE TABLE Rapports (
    idRapport VARCHAR(255) PRIMARY KEY,
    idDossier VARCHAR(255) NOT NULL,
    dateRapport DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    titre VARCHAR(255) NOT NULL,
    statut VARCHAR(50) NOT NULL DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'Finalisé', 'Validé')),
    contenu TEXT,
    statutConformite VARCHAR(50) DEFAULT 'Non évalué' CHECK (statutConformite IN ('Conforme', 'Non Conforme', 'Non évalué')),
    niveauConformite INT CHECK (niveauConformite >= 0 AND niveauConformite <= 100),
    FOREIGN KEY (idDossier) REFERENCES DossiersMedicaux(idDossier) ON UPDATE CASCADE ON DELETE NO ACTION
);

-- Table: ReglesConformite
CREATE TABLE ReglesConformite (
    idRegle VARCHAR(255) PRIMARY KEY,
    descriptionRegle TEXT NOT NULL,
    typeRegle VARCHAR(255) NOT NULL CHECK (typeRegle IN ('Médicale', 'Administrative', 'RGPD', 'HIPAA', 'CDP')),
    niveauCritique VARCHAR(50) NOT NULL CHECK (niveauCritique IN ('Faible', 'Moyen', 'Élevé')),
    dateCreation DATETIME DEFAULT CURRENT_TIMESTAMP,
    estActive BOOLEAN DEFAULT TRUE
);

-- Table: ParametresConformite
CREATE TABLE ParametresConformite (
    idParametre VARCHAR(255) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    seuilMin DECIMAL(10,2),
    seuilMax DECIMAL(10,2),
    unite VARCHAR(50),
    description TEXT,
    idRegle VARCHAR(255),
    FOREIGN KEY (idRegle) REFERENCES ReglesConformite(idRegle) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Prescriptions
CREATE TABLE Prescriptions (
    idPrescription VARCHAR(255) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    typePrescription VARCHAR(255),
    emplacement VARCHAR(255),
    datePrescription DATE NOT NULL,
    situationFinance BOOLEAN DEFAULT FALSE,
    revenu DECIMAL(10,2),
    ficheRevenu VARCHAR(255),
    idDossier VARCHAR(255),
    FOREIGN KEY (idDossier) REFERENCES DossiersMedicaux(idDossier) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Logements
CREATE TABLE Logements (
    idLogement VARCHAR(255) PRIMARY KEY,
    typeLogement VARCHAR(255),
    nombrePersonnesFoyer INT,
    statutOccupation VARCHAR(50) CHECK (statutOccupation IN ('Propriétaire', 'Locataire', 'Hébergé', 'Autre')),
    modePaiementCouverts VARCHAR(255),
    toilettesInterieures BOOLEAN,
    idPatient VARCHAR(255),
    FOREIGN KEY (typeLogement) REFERENCES TypesLogement(idTypeLogement) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Comportements
CREATE TABLE Comportements (
    idComportement VARCHAR(255) PRIMARY KEY,
    viePrivee VARCHAR(255),
    mangerSeulAilleurs VARCHAR(255),
    vieNiveauHabitantAideManager VARCHAR(255),
    utilisationSalonee VARCHAR(255),
    lieuDeNaissanceEnfants VARCHAR(255),
    utilisationEauHydricole VARCHAR(255),
    idPatient VARCHAR(255),
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Alimentations
CREATE TABLE Alimentations (
    idAlimentation VARCHAR(255) PRIMARY KEY,
    regimeAlimentaire VARCHAR(255),
    eauPotable BOOLEAN,
    repas VARCHAR(255),
    typeRepas VARCHAR(255),
    idPatient VARCHAR(255),
    FOREIGN KEY (regimeAlimentaire) REFERENCES RegimesAlimentaires(idRegimeAlimentaire) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Residences
CREATE TABLE Residences (
    idResidence VARCHAR(255) PRIMARY KEY,
    ville VARCHAR(255),
    region VARCHAR(255),
    quartier VARCHAR(255),
    adresseComplete VARCHAR(255),
    idPatient VARCHAR(255),
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Vaccins
CREATE TABLE Vaccins (
    idVaccin VARCHAR(255) PRIMARY KEY,
    nomVaccin VARCHAR(255) NOT NULL,
    description TEXT,
    typeVaccination VARCHAR(255),
    dose VARCHAR(50),
    idPatient VARCHAR(255),
    dateVaccination DATE,
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Infections
CREATE TABLE Infections (
    idInfection VARCHAR(255) PRIMARY KEY,
    nomInfection VARCHAR(255) NOT NULL,
    description TEXT,
    typeInfection VARCHAR(255),
    idPatient VARCHAR(255),
    dateDiagnostic DATE,
    statut VARCHAR(50) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Guéri', 'En traitement')),
    FOREIGN KEY (idPatient) REFERENCES Patients(idPatient) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Alertes
CREATE TABLE Alertes (
    idAlerte VARCHAR(255) PRIMARY KEY,
    typeAlerte VARCHAR(255) NOT NULL CHECK (typeAlerte IN ('Urgent', 'Information', 'Avertissement')),
    message TEXT NOT NULL,
    dateAlerte DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    idUtilisateur VARCHAR(255),
    idDossier VARCHAR(255),
    statut VARCHAR(50) DEFAULT 'Non lu' CHECK (statut IN ('Non lu', 'Lu', 'Traité')),
    FOREIGN KEY (idUtilisateur) REFERENCES Utilisateurs(idUtilisateur) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (idDossier) REFERENCES DossiersMedicaux(idDossier) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: Analyses
CREATE TABLE Analyses (
    idAnalyse VARCHAR(255) PRIMARY KEY,
    designation VARCHAR(255) NOT NULL,
    typeAnalyse VARCHAR(255),
    dateAnalyse DATE NOT NULL,
    idDossier VARCHAR(255),
    statut VARCHAR(50) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Terminé', 'Annulé')),
    FOREIGN KEY (idDossier) REFERENCES DossiersMedicaux(idDossier) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Table: ResultatsAnalyses
CREATE TABLE ResultatsAnalyses (
    idResultat VARCHAR(255) PRIMARY KEY,
    idAnalyse VARCHAR(255) NOT NULL,
    dateResultat DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    poids DECIMAL(5,2),
    tension DECIMAL(5,2),
    temperature DECIMAL(4,2),
    pressionDiastolique DECIMAL(5,2),
    pressionSystolique DECIMAL(5,2),
    globulesBlancs DECIMAL(8,2),
    globulesRouges DECIMAL(8,2),
    lymphocytes DECIMAL(5,2),
    neutrophiles DECIMAL(5,2),
    commentaires TEXT,
    FOREIGN KEY (idAnalyse) REFERENCES Analyses(idAnalyse) ON UPDATE CASCADE ON DELETE NO ACTION
);

-- =====================================================
-- TABLES D'ASSOCIATION
-- =====================================================

-- Table: AccesEtablissements
CREATE TABLE AccesEtablissements (
    idAcces VARCHAR(255) PRIMARY KEY,
    idUtilisateur VARCHAR(255) NOT NULL,
    idEtablissement VARCHAR(255) NOT NULL,
    typeAcces VARCHAR(50) NOT NULL CHECK (typeAcces IN ('Lecture', 'Ecriture', 'Admin')),
    dateAcces DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dateExpiration DATETIME,
    FOREIGN KEY (idUtilisateur) REFERENCES Utilisateurs(idUtilisateur) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (idEtablissement) REFERENCES Etablissements(idEtablissement) ON UPDATE CASCADE ON DELETE NO ACTION,
    UNIQUE(idUtilisateur, idEtablissement)
);

-- Table: DossiersConformiteRegles
CREATE TABLE DossiersConformiteRegles (
    idDossier VARCHAR(255) NOT NULL,
    idRegle VARCHAR(255) NOT NULL,
    dateApplication DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resultatConformite BOOLEAN NOT NULL,
    commentaire TEXT,
    PRIMARY KEY (idDossier, idRegle),
    FOREIGN KEY (idDossier) REFERENCES DossiersMedicaux(idDossier) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (idRegle) REFERENCES ReglesConformite(idRegle) ON UPDATE CASCADE ON DELETE NO ACTION
);

-- =====================================================
-- INDEX POUR OPTIMISER LES PERFORMANCES
-- =====================================================

-- Index sur les clés étrangères
CREATE INDEX idx_patients_niveau_etude ON Patients(niveauEtude);
CREATE INDEX idx_patients_etablissement ON Patients(etablissement);
CREATE INDEX idx_dossiers_patient ON DossiersMedicaux(idPatient);
CREATE INDEX idx_dossiers_utilisateur ON DossiersMedicaux(idUtilisateur);
CREATE INDEX idx_rapports_dossier ON Rapports(idDossier);
CREATE INDEX idx_prescriptions_dossier ON Prescriptions(idDossier);
CREATE INDEX idx_logements_patient ON Logements(idPatient);
CREATE INDEX idx_comportements_patient ON Comportements(idPatient);
CREATE INDEX idx_alimentations_patient ON Alimentations(idPatient);
CREATE INDEX idx_residences_patient ON Residences(idPatient);
CREATE INDEX idx_vaccins_patient ON Vaccins(idPatient);
CREATE INDEX idx_infections_patient ON Infections(idPatient);
CREATE INDEX idx_alertes_utilisateur ON Alertes(idUtilisateur);
CREATE INDEX idx_alertes_dossier ON Alertes(idDossier);
CREATE INDEX idx_analyses_dossier ON Analyses(idDossier);
CREATE INDEX idx_resultats_analyse ON ResultatsAnalyses(idAnalyse);
CREATE INDEX idx_acces_utilisateur ON AccesEtablissements(idUtilisateur);
CREATE INDEX idx_acces_etablissement ON AccesEtablissements(idEtablissement);
CREATE INDEX idx_parametres_regle ON ParametresConformite(idRegle);

-- Index sur les dates pour les requêtes temporelles
CREATE INDEX idx_utilisateurs_date_creation ON Utilisateurs(dateCreation);
CREATE INDEX idx_patients_date_creation ON Patients(dateCreation);
CREATE INDEX idx_dossiers_date_creation ON DossiersMedicaux(dateCreation);
CREATE INDEX idx_rapports_date_rapport ON Rapports(dateRapport);
CREATE INDEX idx_alertes_date_alerte ON Alertes(dateAlerte);
CREATE INDEX idx_analyses_date_analyse ON Analyses(dateAnalyse);
CREATE INDEX idx_resultats_date_resultat ON ResultatsAnalyses(dateResultat);

-- Index sur les statuts pour les filtres
CREATE INDEX idx_utilisateurs_est_active ON Utilisateurs(estActive);
CREATE INDEX idx_dossiers_statut ON DossiersMedicaux(statut);
CREATE INDEX idx_rapports_statut ON Rapports(statut);
CREATE INDEX idx_alertes_statut ON Alertes(statut);
CREATE INDEX idx_analyses_statut ON Analyses(statut);

-- =====================================================
-- DONNEES DE REFERENCE INITIALES
-- =====================================================

-- Insertion des niveaux d'études
INSERT INTO NiveauxEtudes (idNiveauEtude, libelle, description) VALUES
('NE001', 'Primaire', 'Études primaires'),
('NE002', 'Secondaire', 'Études secondaires'),
('NE003', 'Supérieur', 'Études supérieures'),
('NE004', 'Aucun', 'Aucun niveau d''étude');

-- Insertion des types de logement
INSERT INTO TypesLogement (idTypeLogement, libelle, description) VALUES
('TL001', 'Maison individuelle', 'Maison individuelle'),
('TL002', 'Appartement', 'Appartement'),
('TL003', 'Chambre individuelle', 'Chambre individuelle'),
('TL004', 'Logement collectif', 'Logement collectif');

-- Insertion des régimes alimentaires
INSERT INTO RegimesAlimentaires (idRegimeAlimentaire, libelle, description) VALUES
('RA001', 'Normal', 'Régime alimentaire normal'),
('RA002', 'Végétarien', 'Régime végétarien'),
('RA003', 'Sans gluten', 'Régime sans gluten'),
('RA004', 'Diabétique', 'Régime pour diabétiques');

-- Insertion d'un établissement de test
INSERT INTO Etablissements (idEtablissement, nomEtablissement, adresse, telephone, email) VALUES
('ETAB001', 'Centre Médical Principal', '123 Avenue de la Santé, Dakar', '+221 33 123 45 67', 'contact@cmp.sn');

-- Insertion d'un utilisateur administrateur
INSERT INTO Utilisateurs (idUtilisateur, dateCreation, motDePasse, role, nom, prenom, estActive, email) VALUES
('ADMIN001', CURRENT_TIMESTAMP, 'hashed_password_here', 'administrateur', 'Admin', 'Principal', TRUE, 'admin@cmp.sn');

-- Insertion de règles de conformité de base
INSERT INTO ReglesConformite (idRegle, descriptionRegle, typeRegle, niveauCritique) VALUES
('RGPD001', 'Consentement explicite pour le traitement des données personnelles', 'RGPD', 'Élevé'),
('HIPAA001', 'Protection des informations de santé personnelles', 'HIPAA', 'Élevé'),
('CDP001', 'Respect du code de déontologie sénégalais', 'CDP', 'Moyen'),
('MED001', 'Validation médicale obligatoire des dossiers', 'Médicale', 'Élevé');

-- =====================================================
-- COMMENTAIRES FINAUX
-- =====================================================

/*
STRUCTURE DE BASE DE DONNEES TERMINEE

Cette base de données supporte :
- Gestion des patients et dossiers médicaux
- Suivi de la conformité RGPD/HIPAA/CDP
- Système d'alertes et de rapports
- Gestion multi-établissements
- Audit trail complet
- Sécurité et traçabilité

Prochaines étapes :
1. Implémentation dans Django avec les modèles
2. Création des sérialiseurs API
3. Développement du tableau de bord React
4. Tests de sécurité et conformité
*/ 