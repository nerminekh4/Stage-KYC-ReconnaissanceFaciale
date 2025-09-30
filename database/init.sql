CREATE TABLE kyc_verifications (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    prenom TEXT,
    date_naissance DATE,
    statut TEXT,
    commentaire TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
