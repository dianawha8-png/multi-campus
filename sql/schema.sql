-- =====================================================================
-- SCHEMA SUPABASE — Consolidation des notes multi-campus
-- A exécuter dans Supabase > SQL Editor > New query
-- =====================================================================

-- Extension pour UUID
create extension if not exists "pgcrypto";

-- =====================================================================
-- TABLE PRINCIPALE : NOTES_CENTRALES
-- =====================================================================
create table if not exists notes_centrales (
    id                      uuid primary key default gen_random_uuid(),
    matricule               text,
    nom                     text not null,
    prenoms                 text not null,
    classe_texte            text not null,
    campus_texte            text not null,
    semestre_texte          text,
    formation_texte         text,               -- BTS / Licence / Master
    ue                      text not null,
    enseignant              text,
    note1                   numeric(5,2),
    note2                   numeric(5,2),
    moyenne                 numeric(5,4),
    nom_fichier_source      text not null,
    cle_import              text not null,
    date_import             timestamptz not null default now(),
    derniere_modification   timestamptz not null default now(),

    constraint uq_notes_cle_import unique (cle_import, ue)
);

comment on table notes_centrales is 'Table centrale de toutes les notes importées, tous campus confondus';
comment on column notes_centrales.cle_import is 'matricule|nom|prenoms|classe (ou *|nom|prenoms|classe si matricule vide)';

-- Index de recherche
create index if not exists idx_notes_matricule   on notes_centrales (matricule);
create index if not exists idx_notes_nom         on notes_centrales (nom);
create index if not exists idx_notes_prenoms     on notes_centrales (prenoms);
create index if not exists idx_notes_classe      on notes_centrales (classe_texte);
create index if not exists idx_notes_campus      on notes_centrales (campus_texte);
create index if not exists idx_notes_ue          on notes_centrales (ue);
create index if not exists idx_notes_enseignant  on notes_centrales (enseignant);
create index if not exists idx_notes_cle_import  on notes_centrales (cle_import);

-- Trigger : mise à jour automatique de derniere_modification
create or replace function set_derniere_modification()
returns trigger as $$
begin
    new.derniere_modification = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_notes_maj on notes_centrales;
create trigger trg_notes_maj
    before update on notes_centrales
    for each row
    execute function set_derniere_modification();

-- =====================================================================
-- TABLE : FICHIERS_IMPORT (journal des imports)
-- =====================================================================
create table if not exists fichiers_import (
    id                  uuid primary key default gen_random_uuid(),
    nom_fichier         text not null,
    campus_detecte      text,
    semestre_detecte    text,
    nb_feuilles         integer default 0,
    nb_lignes_lues      integer default 0,
    nb_lignes_inserees  integer default 0,
    nb_lignes_maj       integer default 0,
    nb_erreurs          integer default 0,
    date_import         timestamptz not null default now(),
    importe_par         text
);

create index if not exists idx_fichiers_date on fichiers_import (date_import desc);

-- =====================================================================
-- TABLE : JOURNAL_ERREURS
-- =====================================================================
create table if not exists journal_erreurs (
    id              uuid primary key default gen_random_uuid(),
    fichier_import_id uuid references fichiers_import(id) on delete cascade,
    nom_fichier     text not null,
    feuille         text,
    ligne_excel     integer,
    type_erreur     text not null,   -- 'ligne_vide' | 'matricule_absent' | 'doublon' | 'feuille_vide' | 'fichier_vide' | 'colonnes_manquantes'
    detail          text,
    date_creation   timestamptz not null default now()
);

create index if not exists idx_erreurs_type on journal_erreurs (type_erreur);
create index if not exists idx_erreurs_fichier on journal_erreurs (fichier_import_id);

-- =====================================================================
-- TABLE : PARAMETRES (référentiels modifiables depuis l'app)
-- =====================================================================
create table if not exists parametres_campus (
    id      uuid primary key default gen_random_uuid(),
    nom     text not null unique
);

insert into parametres_campus (nom)
select v from (values ('PLATEAU'), ('YOPOUGON'), ('YAMOUSSOUKRO')) as t(v)
on conflict (nom) do nothing;

create table if not exists parametres_formations (
    id      uuid primary key default gen_random_uuid(),
    nom     text not null unique
);

insert into parametres_formations (nom)
select v from (values ('BTS'), ('LICENCE'), ('MASTER')) as t(v)
on conflict (nom) do nothing;

-- =====================================================================
-- VUES UTILES
-- =====================================================================

-- Vue Etudiants : un étudiant = regroupement par matricule (ou nom+prenoms si matricule vide)
create or replace view v_etudiants as
select
    coalesce(nullif(matricule, ''), '*') as matricule,
    nom,
    prenoms,
    classe_texte,
    campus_texte,
    count(*)                     as nb_ue,
    round(avg(moyenne), 2)       as moyenne_generale,
    max(derniere_modification)   as derniere_maj
from notes_centrales
group by matricule, nom, prenoms, classe_texte, campus_texte;

-- Vue Enseignants (extrait du nom de fichier, convention CAMPUS-SEMESTRE-NOM.xlsx)
create or replace view v_enseignants as
select
    enseignant,
    count(distinct ue)            as nb_ue,
    count(distinct classe_texte)  as nb_classes,
    count(*)                      as nb_notes_saisies,
    round(avg(moyenne), 2)        as moyenne_donnee
from notes_centrales
where enseignant is not null
group by enseignant;

-- Vue Moyenne par classe
create or replace view v_moyenne_par_classe as
select classe_texte, campus_texte, round(avg(moyenne), 2) as moyenne, count(*) as nb_notes
from notes_centrales
group by classe_texte, campus_texte
order by classe_texte;

-- Vue Moyenne par UE
create or replace view v_moyenne_par_ue as
select ue, round(avg(moyenne), 2) as moyenne, count(*) as nb_notes
from notes_centrales
group by ue
order by ue;

-- Vue Moyenne par campus
create or replace view v_moyenne_par_campus as
select campus_texte, round(avg(moyenne), 2) as moyenne, count(*) as nb_notes,
       count(distinct classe_texte) as nb_classes
from notes_centrales
group by campus_texte;

-- Vue Etudiants sans matricule
create or replace view v_etudiants_sans_matricule as
select * from notes_centrales
where matricule is null or matricule = '';

-- Vue Etudiants sans note
create or replace view v_etudiants_sans_note as
select * from notes_centrales
where note1 is null and note2 is null;

-- Vue Classement des étudiants (par classe, sur la moyenne générale)
create or replace view v_classement_etudiants as
select
    matricule, nom, prenoms, classe_texte, campus_texte,
    round(avg(moyenne), 2) as moyenne_generale,
    rank() over (partition by classe_texte order by avg(moyenne) desc) as rang
from notes_centrales
group by matricule, nom, prenoms, classe_texte, campus_texte;

-- Vue tableau de bord (compteurs globaux)
create or replace view v_tableau_de_bord as
select
    (select count(distinct coalesce(nullif(matricule,''), nom || prenoms || classe_texte)) from notes_centrales) as nb_etudiants,
    (select count(*) from notes_centrales) as nb_notes,
    (select count(distinct enseignant) from notes_centrales where enseignant is not null) as nb_enseignants,
    (select count(distinct ue) from notes_centrales) as nb_ue,
    (select count(distinct classe_texte) from notes_centrales) as nb_classes,
    (select count(distinct campus_texte) from notes_centrales) as nb_campus;

-- =====================================================================
-- ROW LEVEL SECURITY (désactivé par défaut — clé service_role côté serveur
-- Streamlit uniquement, jamais exposée au navigateur)
-- =====================================================================
alter table notes_centrales enable row level security;
alter table fichiers_import enable row level security;
alter table journal_erreurs enable row level security;

-- Politique : accès total via clé service_role (utilisée uniquement côté serveur)
create policy "service_role_full_access_notes" on notes_centrales
    for all using (true) with check (true);
create policy "service_role_full_access_fichiers" on fichiers_import
    for all using (true) with check (true);
create policy "service_role_full_access_erreurs" on journal_erreurs
    for all using (true) with check (true);

-- =====================================================================
-- FIN DU SCRIPT
-- =====================================================================
