# =============================================================================
# SCRIPT R : modelisation de l'Effet de la salinite de l'eau d'irrigation sur 
# la germination et la croissance initiale du haricot  (Phaseolus vulgaris L.)
# Dispositif en Blocs Complets Randomises (DBCR) : 3 blocs x 5 doses
# Auteur     : Charles Baraka Nteranya
# Date       : Juillet 2025
# =============================================================================
# CHANGEMENTS v3:
#  - Palette unique degradee (bleu ciel -> cyan -> jaune -> orange -> rouge)
#    utilisee sur TOUTES les figures (coherence visuelle globale)
#  - Police Roboto (Google Fonts, via showtext) appliquee partout, y
#    compris dans le corrplot en graphiques de base
#  - Nouveau theme "theme_salinite" : fond creme doux, grille horizontale
#    en pointilles uniquement, axes fins, titres alignes a gauche
#  - Fig. 2 a 5 : boxplots enrichis (jitter + losange de moyenne + lettres
#    CLD) accompagnes d'un mini-tableau recapitulatif (n, moyenne, ET)
#    sous chaque graphique, a la maniere de ggpubr::ggsummarystats()
#  - Fig. 8 : ajout d'une densite marginale (a droite) de la germination
#    par dose, dans l'esprit d'un scatter + densites marginales
#  - Fig. 9 : degrade de couleurs recale sur la meme famille (orange <-> 
#    bleu ciel) au lieu du rouge/vert d'origine
# =============================================================================

# =============================================================================
# 0.  CONFIGURATION GENERALE : PALETTE, POLICE, CHEMINS
# =============================================================================

OUTPUT_DIR <- "D:/SolM2"

if (!dir.exists(OUTPUT_DIR))       dir.create(OUTPUT_DIR, recursive = TRUE)
dir.create(file.path(OUTPUT_DIR, "figures"),  showWarnings = FALSE)
dir.create(file.path(OUTPUT_DIR, "tableaux"), showWarnings = FALSE)

# ---- Palette unique (degrade bleu ciel -> cyan -> jaune -> orange -> rouge)
# Utilisee pour TOUTES les figures : coherence visuelle + lecture intuitive
# de l'intensite croissante du stress salin (0 -> 45 g/L)
PALETTE_DOSE <- c(
  "0"  = "#0EA5E9",   # bleu ciel   — temoin
  "5"  = "#2DD4CF",   # cyan/teal
  "15" = "#FBBF24",   # jaune
  "30" = "#FB923C",   # orange
  "45" = "#EF4444"    # rouge       — stress severe
)
DOSE_LABELS <- c("0"="0 g/L (Temoin)", "5"="5 g/L", "15"="15 g/L",
                 "30"="30 g/L",        "45"="45 g/L")

FONT_MAIN <- "Roboto"

# =============================================================================
# 1.  INSTALLATION CONDITIONNELLE ET CHARGEMENT DES PACKAGES
# =============================================================================

packages_requis <- c(
  "readxl",        # import Excel
  "openxlsx",      # export Excel avec mise en forme
  "dplyr",         # manipulation donnees
  "tidyr",         # pivotement tableaux
  "ggplot2",       # visualisation
  "ggpubr",        # extensions ggplot2 (ggsummarytable, clean_table_theme)
  "rstatix",       # statistiques descriptives par groupe (get_summary_stats)
  "RColorBrewer",  # palettes couleurs
  "corrplot",      # matrice correlation (base graphics)
  "ggcorrplot",    # matrice correlation (ggplot2)
  "car",           # test de Levene
  "emmeans",       # moyennes marginales + Tukey
  "multcomp",      # groupes homogenes CLD
  "multcompView",  # lettres CLD
  "lme4",          # modeles mixtes
  "lmerTest",      # p-values modeles mixtes
  "nortest",       # tests normalite
  "scales",        # formatage axes
  "patchwork",     # assemblage figures
  "broom",         # tidying sorties modeles
  "showtext"       # police Roboto dans tous les graphiques
)

for (pkg in packages_requis) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    message("Installation : ", pkg)
    install.packages(pkg, repos = "https://cran.r-project.org", dependencies = TRUE)
  }
  suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}

# Forcer dplyr en premier plan apres chargement de tous les packages
# (neutralise les masquages par MASS, car, etc.)
suppressMessages({
  library(dplyr)
  library(ggplot2)
})

# ---- Activation de la police Roboto pour TOUS les graphiques --------------
sysfonts::font_add_google("Roboto", "Roboto")
showtext::showtext_auto()
showtext::showtext_opts(dpi = 300)

message("\n\u2713 Tous les packages sont charges (police Roboto active).\n")

# =============================================================================
# 2.  IMPORT DES DONNEES
# =============================================================================

FICHIER_DATA <- file.path(OUTPUT_DIR, "data.xlsx")

if (!file.exists(FICHIER_DATA)) {
  stop("Fichier introuvable : ", FICHIER_DATA,
       "\nCopiez votre fichier Excel dans D:/SolM2 et nommez-le 'data.xlsx'.")
}

suivi_raw     <- readxl::read_excel(FICHIER_DATA, sheet = "Suivi_quotidien")
final_raw     <- readxl::read_excel(FICHIER_DATA, sheet = "Mesures_finales")
solutions_raw <- readxl::read_excel(FICHIER_DATA, sheet = "Solutions_meres")

message("\u2713 Donnees importees depuis : ", FICHIER_DATA)

# =============================================================================
# 3.  NETTOYAGE ET PREPARATION DES DONNEES
# =============================================================================

NIVEAUX_DOSE <- c("0", "5", "15", "30", "45")

# ---- 3.1  Suivi quotidien --------------------------------------------------
suivi <- suivi_raw %>%
  dplyr::rename(
    Taux_Germination = Taux_Germination_pct
  ) %>%
  dplyr::mutate(
    Dose_gL          = factor(as.character(Dose_gL), levels = NIVEAUX_DOSE),
    Bloc             = as.factor(Bloc),
    Pot_ID           = as.factor(Pot_ID),
    Jour             = as.integer(Jour),
    Taux_Germination = as.numeric(Taux_Germination),
    Longueur_Tige_mm = as.numeric(Longueur_Tige_mm),
    Nb_Feuilles      = as.numeric(Nb_Feuilles),
    Graines_Germees  = as.numeric(Graines_Germees),
    Etat_Visuel      = as.factor(Etat_Visuel)
  )

# ---- 3.2  Longueur de tige au J21 par pot (calculee avant final) -----------
tige_j21_par_pot <- suivi %>%
  dplyr::filter(Jour == 21) %>%
  dplyr::group_by(Pot_ID) %>%
  dplyr::summarise(Longueur_Tige_J21_mm = mean(Longueur_Tige_mm, na.rm = TRUE),
                   .groups = "drop")

# ---- 3.3  Mesures finales --------------------------------------------------
final <- final_raw %>%
  dplyr::mutate(
    Dose_gL              = factor(as.character(Dose_gL), levels = NIVEAUX_DOSE),
    Bloc                 = as.factor(Bloc),
    Pot_ID               = as.factor(Pot_ID),
    Nb_Plants_J21        = as.numeric(Nb_Plants_J21),
    Longueur_Racine_mm   = as.numeric(Longueur_Racine_mm),
    Surface_Foliaire_cm2 = as.numeric(Surface_Foliaire_cm2),
    CE_Sol_Final_dSm     = as.numeric(CE_Sol_Final_dSm),
    Taux_Germination_J21 = round(Nb_Plants_J21 / 9 * 100, 1)
  ) %>%
  dplyr::left_join(tige_j21_par_pot, by = "Pot_ID") %>%
  dplyr::mutate(
    Ratio_Racine_Tige = dplyr::if_else(
      !is.na(Longueur_Tige_J21_mm) & Longueur_Tige_J21_mm > 0,
      round(Longueur_Racine_mm / Longueur_Tige_J21_mm, 3),
      NA_real_
    )
  )

# ---- 3.4  Donnees J21 consolidees (jointure suivi J21 + mesures finales) ---
data_j21 <- suivi %>%
  dplyr::filter(Jour == 21) %>%
  dplyr::left_join(
    final %>% dplyr::select(
      Pot_ID, Nb_Plants_J21, Longueur_Racine_mm,
      Surface_Foliaire_cm2, CE_Sol_Final_dSm,
      Taux_Germination_J21, Ratio_Racine_Tige
    ),
    by = "Pot_ID"
  ) %>%
  dplyr::mutate(
    Dose_num = as.numeric(as.character(Dose_gL)),
    CE_dSm   = CE_Sol_Final_dSm
  )

# ---- 3.5  CE theorique par dose -------------------------------------------
CE_ref <- solutions_raw %>%
  dplyr::select(Dose_gL, CE_theorique_dSm, Concentration_mM) %>%
  dplyr::mutate(Dose_gL = factor(as.character(Dose_gL), levels = NIVEAUX_DOSE))

message("\u2713 Donnees nettoyees et structurees.")

# =============================================================================
# 4.  STATISTIQUES DESCRIPTIVES
# =============================================================================

desc_germ <- data_j21 %>%
  dplyr::group_by(Dose_gL) %>%
  dplyr::summarise(
    N             = dplyr::n(),
    Germ_Moy_pct  = round(mean(Taux_Germination_J21, na.rm = TRUE), 2),
    Germ_SD       = round(sd(Taux_Germination_J21,   na.rm = TRUE), 2),
    Germ_Min      = min(Taux_Germination_J21,         na.rm = TRUE),
    Germ_Max      = max(Taux_Germination_J21,         na.rm = TRUE),
    Tige_Moy_mm   = round(mean(Longueur_Tige_mm,      na.rm = TRUE), 2),
    Tige_SD_mm    = round(sd(Longueur_Tige_mm,        na.rm = TRUE), 2),
    Racine_Moy_mm = round(mean(Longueur_Racine_mm,    na.rm = TRUE), 2),
    Racine_SD_mm  = round(sd(Longueur_Racine_mm,      na.rm = TRUE), 2),
    Feuilles_Moy  = round(mean(Nb_Feuilles,           na.rm = TRUE), 2),
    Ratio_R_T_Moy = round(mean(Ratio_Racine_Tige,     na.rm = TRUE), 3),
    .groups = "drop"
  ) %>%
  dplyr::left_join(CE_ref, by = "Dose_gL") %>%
  dplyr::mutate(
    STI_pct = round(Germ_Moy_pct /
                      Germ_Moy_pct[Dose_gL == "0"] * 100, 2)
  )

cat("\n=== STATISTIQUES DESCRIPTIVES J21 ===\n")
print(as.data.frame(desc_germ))

# =============================================================================
# 5.  TESTS STATISTIQUES
# =============================================================================

# ---- 5.1  Normalite des residus (Shapiro-Wilk) ----------------------------
test_sw <- function(formule_chr, nom, data) {
  mod <- lm(as.formula(formule_chr), data = data)
  sw  <- shapiro.test(residuals(mod))
  cat(sprintf("[Shapiro-Wilk] %-35s W=%.4f  p=%.4f  %s\n",
              nom, sw$statistic, sw$p.value,
              ifelse(sw$p.value > 0.05, "\u2713 normal", "! non-normal")))
  invisible(sw)
}

cat("\n=== TESTS DE NORMALITE (residus) ===\n")
sw_germ   <- test_sw("Taux_Germination_J21 ~ Dose_gL + Bloc", "Taux germination",   data_j21)
sw_tige   <- test_sw("Longueur_Tige_mm     ~ Dose_gL + Bloc", "Longueur tige",      data_j21)
sw_racine <- test_sw("Longueur_Racine_mm   ~ Dose_gL + Bloc", "Longueur racine",    data_j21)
sw_feui   <- test_sw("Nb_Feuilles          ~ Dose_gL + Bloc", "Nombre de feuilles", data_j21)

# ---- 5.2  Homogeneite des variances (Levene) ------------------------------
cat("\n=== TEST DE LEVENE (homogeneite des variances) ===\n")
lev_germ   <- car::leveneTest(Taux_Germination_J21 ~ Dose_gL, data = data_j21)
lev_tige   <- car::leveneTest(Longueur_Tige_mm     ~ Dose_gL, data = data_j21)
lev_racine <- car::leveneTest(Longueur_Racine_mm   ~ Dose_gL, data = data_j21)
cat("Germination :\n"); print(lev_germ)
cat("Tige        :\n"); print(lev_tige)
cat("Racine      :\n"); print(lev_racine)

# ---- 5.3  ANOVA DBCR (modele mixte : Bloc = effet aleatoire) -------------
cat("\n=== ANOVA DBCR (modele mixte) ===\n")

mod_germ   <- lmerTest::lmer(Taux_Germination_J21 ~ Dose_gL + (1|Bloc), data = data_j21)
mod_tige   <- lmerTest::lmer(Longueur_Tige_mm     ~ Dose_gL + (1|Bloc), data = data_j21)
mod_racine <- lmerTest::lmer(Longueur_Racine_mm   ~ Dose_gL + (1|Bloc), data = data_j21)
mod_feui   <- lmerTest::lmer(Nb_Feuilles          ~ Dose_gL + (1|Bloc), data = data_j21)
mod_ratio  <- lmerTest::lmer(Ratio_Racine_Tige    ~ Dose_gL + (1|Bloc), data = data_j21)

aov_germ   <- anova(mod_germ)
aov_tige   <- anova(mod_tige)
aov_racine <- anova(mod_racine)
aov_feui   <- anova(mod_feui)
aov_ratio  <- anova(mod_ratio)

cat("-- Germination --\n");  print(aov_germ)
cat("-- Tige --\n");         print(aov_tige)
cat("-- Racine --\n");       print(aov_racine)
cat("-- Feuilles --\n");     print(aov_feui)
cat("-- Ratio R/T --\n");    print(aov_ratio)

# ---- 5.4  Comparaisons multiples Tukey + lettres CLD ----------------------
cat("\n=== COMPARAISONS MULTIPLES (Tukey HSD) ===\n")

em_germ   <- emmeans::emmeans(mod_germ,   pairwise ~ Dose_gL, adjust = "tukey")
em_tige   <- emmeans::emmeans(mod_tige,   pairwise ~ Dose_gL, adjust = "tukey")
em_racine <- emmeans::emmeans(mod_racine, pairwise ~ Dose_gL, adjust = "tukey")
em_feui   <- emmeans::emmeans(mod_feui,   pairwise ~ Dose_gL, adjust = "tukey")

cld_germ   <- multcomp::cld(em_germ$emmeans,   Letters = letters, alpha = 0.05) %>%
  as.data.frame() %>% dplyr::mutate(Dose_gL = as.character(Dose_gL))
cld_tige   <- multcomp::cld(em_tige$emmeans,   Letters = letters, alpha = 0.05) %>%
  as.data.frame() %>% dplyr::mutate(Dose_gL = as.character(Dose_gL))
cld_racine <- multcomp::cld(em_racine$emmeans, Letters = letters, alpha = 0.05) %>%
  as.data.frame() %>% dplyr::mutate(Dose_gL = as.character(Dose_gL))
cld_feui   <- multcomp::cld(em_feui$emmeans,   Letters = letters, alpha = 0.05) %>%
  as.data.frame() %>% dplyr::mutate(Dose_gL = as.character(Dose_gL))

cat("CLD Germination :\n"); print(cld_germ)
cat("CLD Tige :\n");        print(cld_tige)
cat("CLD Racine :\n");      print(cld_racine)
cat("CLD Feuilles :\n");    print(cld_feui)

# ---- 5.5  Regressions dose-reponse ----------------------------------------
cat("\n=== REGRESSIONS DOSE-REPONSE ===\n")

reg_germ    <- lm(Taux_Germination_J21 ~ Dose_num,                    data = data_j21)
reg_germ_q  <- lm(Taux_Germination_J21 ~ Dose_num + I(Dose_num^2),   data = data_j21)
reg_tige    <- lm(Longueur_Tige_mm     ~ Dose_num,                    data = data_j21)
reg_tige_q  <- lm(Longueur_Tige_mm     ~ Dose_num + I(Dose_num^2),   data = data_j21)
reg_racine  <- lm(Longueur_Racine_mm   ~ Dose_num,                    data = data_j21)

cat("Regression germination (lineaire) :\n");   print(summary(reg_germ))
cat("Regression germination (quadratique) :\n"); print(summary(reg_germ_q))
cat("Regression tige (lineaire) :\n");           print(summary(reg_tige))
cat("Regression racine (lineaire) :\n");         print(summary(reg_racine))

# ---- 5.6  Matrice de correlation ------------------------------------------
cat("\n=== MATRICE DE CORRELATION (Pearson) ===\n")

vars_corr <- data_j21 %>%
  dplyr::select(Dose_num, Taux_Germination_J21, Longueur_Tige_mm,
                Longueur_Racine_mm, Nb_Feuilles, Ratio_Racine_Tige,
                Surface_Foliaire_cm2, CE_dSm) %>%
  dplyr::mutate(dplyr::across(dplyr::everything(), as.numeric)) %>%
  dplyr::filter(complete.cases(.))

mat_corr <- cor(vars_corr, method = "pearson", use = "complete.obs")
mat_pval <- ggcorrplot::cor_pmat(vars_corr)

cat("Matrice de correlation :\n")
print(round(mat_corr, 3))

# =============================================================================
# 6.  FIGURES : DESIGN UNIFIE (palette unique + police Roboto)
# =============================================================================

save_fig <- function(nom, plot_obj, w = 18, h = 13, dpi = 300) {
  path <- file.path(OUTPUT_DIR, "figures", paste0(nom, ".png"))
  ggplot2::ggsave(path, plot = plot_obj,
                  width = w, height = h, units = "cm",
                  dpi = dpi, bg = "#FBFAF6")
  message("  \u2713 ", path)
}

# ---- Theme unifie -----------------------------------------------------
# Inspire du style ggstatsplot : fond creme doux, grille horizontale
# uniquement (pointilles), axes fins, titres alignes a gauche, Roboto partout
theme_salinite <- ggplot2::theme_minimal(base_size = 12, base_family = FONT_MAIN) +
  ggplot2::theme(
    plot.title          = ggplot2::element_text(family = FONT_MAIN, face = "bold",
                                                size = 13, color = "#1B2838", hjust = 0),
    plot.subtitle       = ggplot2::element_text(family = FONT_MAIN, size = 9.5,
                                                color = "grey35", hjust = 0),
    plot.title.position = "plot",
    axis.title          = ggplot2::element_text(family = FONT_MAIN, face = "bold",
                                                size = 10.5, color = "black"),
    axis.text           = ggplot2::element_text(family = FONT_MAIN, size = 9.5, color = "black"),
    axis.ticks          = ggplot2::element_blank(),
    axis.line           = ggplot2::element_line(colour = "grey45", linewidth = 0.4),
    panel.grid.major.x  = ggplot2::element_blank(),
    panel.grid.major.y  = ggplot2::element_line(linetype = "dashed", colour = "grey82", linewidth = 0.4),
    panel.grid.minor    = ggplot2::element_blank(),
    panel.background    = ggplot2::element_rect(fill = "#FBFAF6", colour = NA),
    plot.background      = ggplot2::element_rect(fill = "#FBFAF6", colour = NA),
    legend.position      = "bottom",
    legend.title         = ggplot2::element_text(family = FONT_MAIN, face = "bold", size = 9.5),
    legend.text          = ggplot2::element_text(family = FONT_MAIN, size = 9),
    strip.background     = ggplot2::element_rect(fill = "#EFE9DF", colour = NA),
    strip.text           = ggplot2::element_text(family = FONT_MAIN, face = "bold", colour = "#1B2838")
  )

cat("\n=== GENERATION DES FIGURES ===\n")

# -- Calcul des donnees de cinetique (reutilise dans plusieurs figures) ------
germ_cinet <- suivi %>%
  dplyr::group_by(Jour, Dose_gL) %>%
  dplyr::summarise(
    Moy_germ = mean(Taux_Germination, na.rm = TRUE),
    SD_germ  = sd(Taux_Germination,   na.rm = TRUE),
    .groups  = "drop"
  )

tige_temps <- suivi %>%
  dplyr::filter(Longueur_Tige_mm > 0) %>%
  dplyr::group_by(Jour, Dose_gL) %>%
  dplyr::summarise(
    Moy_tige = mean(Longueur_Tige_mm, na.rm = TRUE),
    SD_tige  = sd(Longueur_Tige_mm,   na.rm = TRUE),
    .groups  = "drop"
  )

# -- Hauteur max pour les etiquettes CLD ------------------------------------
ymax_tige   <- max(data_j21$Longueur_Tige_mm,   na.rm = TRUE)
ymax_racine <- max(data_j21$Longueur_Racine_mm,  na.rm = TRUE)
ymax_feui   <- max(data_j21$Nb_Feuilles,         na.rm = TRUE)

# ---- Fonction generique : boxplot enrichi (jitter + moyenne + lettres CLD) -
box_stress <- function(data, yvar, cld_df, ylab, titre, sous_titre, ypos_cld) {
  ggplot2::ggplot(data, ggplot2::aes(x = Dose_gL, y = .data[[yvar]], fill = Dose_gL)) +
    ggplot2::geom_boxplot(alpha = 0.85, width = 0.55, linewidth = 0.5,
                          colour = "grey25", outlier.shape = NA) +
    ggplot2::geom_jitter(width = 0.09, size = 2.3, shape = 21, colour = "grey20",
                         fill = "white", stroke = 0.9, alpha = 0.9) +
    ggplot2::stat_summary(fun = mean, geom = "point", shape = 23, size = 3.2,
                          fill = "white", colour = "grey15", stroke = 1) +
    ggplot2::geom_text(data = cld_df,
                       ggplot2::aes(x = Dose_gL, y = ypos_cld, label = trimws(.group)),
                       inherit.aes = FALSE, family = FONT_MAIN, fontface = "bold",
                       size = 4.3, colour = "#1B2838") +
    ggplot2::scale_fill_manual(values = PALETTE_DOSE, guide = "none") +
    ggplot2::scale_x_discrete(labels = DOSE_LABELS) +
    ggplot2::labs(title = titre, subtitle = sous_titre,
                  x = "Concentration saline (g/L)", y = ylab) +
    theme_salinite
}

# ---- Fonction generique : boxplot + mini-tableau recapitulatif (n, moy, ET)-
# Style inspire de ggpubr::ggsummarystats() / ggarrange(bxp, table)
box_with_table <- function(bxp, data, yvar) {
  stats_tbl <- data %>%
    dplyr::filter(!is.na(.data[[yvar]])) %>%
    dplyr::group_by(Dose_gL) %>%
    rstatix::get_summary_stats(dplyr::all_of(yvar), type = "mean_sd") %>%
    dplyr::mutate(Dose_gL = factor(Dose_gL, levels = NIVEAUX_DOSE)) %>%
    dplyr::arrange(Dose_gL) %>%
    dplyr::select(Dose_gL, n, mean, sd)
  
  tbl <- ggpubr::ggsummarytable(
    stats_tbl, x = "Dose_gL", y = c("n", "mean", "sd"),
    ggtheme = ggplot2::theme_minimal(base_family = FONT_MAIN, base_size = 9)
  ) + ggpubr::clean_table_theme()
  
  patchwork::wrap_plots(bxp, tbl, ncol = 1, heights = c(0.80, 0.20))
}

# ============================================================
# Fig 1. Cinetique de germination
# ============================================================
fig1 <- ggplot2::ggplot(
  germ_cinet,
  ggplot2::aes(x = Jour, y = Moy_germ, color = Dose_gL, group = Dose_gL)) +
  ggplot2::geom_ribbon(
    ggplot2::aes(ymin = pmax(0, Moy_germ - SD_germ),
                 ymax = pmin(100, Moy_germ + SD_germ), fill = Dose_gL),
    alpha = 0.12, color = NA) +
  ggplot2::geom_line(linewidth = 1.2) +
  ggplot2::geom_point(size = 2.6, shape = 21, fill = "white", stroke = 1.2) +
  ggplot2::scale_color_manual(values = PALETTE_DOSE, labels = DOSE_LABELS, name = "Dose de sel") +
  ggplot2::scale_fill_manual( values = PALETTE_DOSE, labels = DOSE_LABELS, name = "Dose de sel") +
  ggplot2::scale_x_continuous(breaks = c(1, 5, 7, 10, 14, 17, 21),
                              labels = c("J1","J5","J7","J10","J14","J17","J21")) +
  ggplot2::scale_y_continuous(limits = c(0, 110), breaks = seq(0, 100, 20),
                              labels = scales::percent_format(scale = 1)) +
  ggplot2::geom_vline(xintercept = 5, linetype = "dashed", color = "grey55", linewidth = 0.5) +
  ggplot2::annotate("text", x = 5.3, y = 108, family = FONT_MAIN,
                    label = "1eres germinations (J5)", size = 3, color = "grey40", hjust = 0) +
  ggplot2::labs(
    title    = "Figure 1 \u2014 Cinetique de germination selon la dose saline",
    subtitle = "Moyenne \u00b1 ecart-type (n = 3 blocs par dose)",
    x = "Jours apres semis", y = "Taux de germination (%)") +
  theme_salinite
save_fig("Fig1_cinetique_germination", fig1, w = 20, h = 13)

# ============================================================
# Fig 2 . Boxplot germination J21 (+ mini-tableau recapitulatif)
# ============================================================
fig2_box <- box_stress(
  data_j21, "Taux_Germination_J21", cld_germ,
  "Taux de germination (%)",
  "Figure 2 \u2014 Taux de germination au J21 selon la concentration saline",
  "Lettres differentes = differences significatives (Tukey HSD, \u03b1 = 0,05)",
  112) +
  ggplot2::scale_y_continuous(limits = c(0, 120), labels = scales::percent_format(scale = 1))
fig2 <- box_with_table(fig2_box, data_j21, "Taux_Germination_J21")
save_fig("Fig2_boxplot_germination_J21", fig2, w = 18, h = 15)

# ============================================================
# Fig 3 . Boxplot longueur de tige J21 (+ mini-tableau)
# ============================================================
data_tige_ok <- data_j21 %>% dplyr::filter(!is.na(Longueur_Tige_mm), Longueur_Tige_mm > 0)
fig3_box <- box_stress(
  data_tige_ok, "Longueur_Tige_mm", cld_tige, "Longueur de tige (mm)",
  "Figure 3 \u2014 Longueur de tige (mm) au J21 selon la concentration saline",
  "Lettres differentes = differences significatives (Tukey HSD, \u03b1 = 0,05)",
  ymax_tige * 1.15)
fig3 <- box_with_table(fig3_box, data_tige_ok, "Longueur_Tige_mm")
save_fig("Fig3_boxplot_tige_J21", fig3, w = 18, h = 15)

# ============================================================
# Fig 4 . Boxplot longueur de racine J21 (+ mini-tableau)
# ============================================================
data_racine_ok <- data_j21 %>% dplyr::filter(!is.na(Longueur_Racine_mm), Longueur_Racine_mm > 0)
fig4_box <- box_stress(
  data_racine_ok, "Longueur_Racine_mm", cld_racine, "Longueur de racine (mm)",
  "Figure 4 \u2014 Longueur de racine (mm) au J21 selon la concentration saline",
  "Lettres differentes = differences significatives (Tukey HSD, \u03b1 = 0,05)",
  ymax_racine * 1.15)
fig4 <- box_with_table(fig4_box, data_racine_ok, "Longueur_Racine_mm")
save_fig("Fig4_boxplot_racine_J21", fig4, w = 18, h = 15)

# ============================================================
# Fig 5 . Boxplot nombre de feuilles J21 (+ mini-tableau)
# ============================================================
fig5_box <- box_stress(
  data_j21, "Nb_Feuilles", cld_feui, "Nombre de feuilles",
  "Figure 5 \u2014 Nombre de feuilles deployees au J21",
  "Lettres differentes = differences significatives (Tukey HSD, \u03b1 = 0,05)",
  ymax_feui + 0.8)
fig5 <- box_with_table(fig5_box, data_j21, "Nb_Feuilles")
save_fig("Fig5_boxplot_feuilles_J21", fig5, w = 18, h = 15)

# ============================================================
# Fig 6 . Ratio racine/tige par dose (barres + erreur)
# ============================================================
ratio_dose <- data_j21 %>%
  dplyr::group_by(Dose_gL) %>%
  dplyr::summarise(
    Ratio_moy = mean(Ratio_Racine_Tige, na.rm = TRUE),
    Ratio_sd  = sd(Ratio_Racine_Tige,   na.rm = TRUE),
    .groups   = "drop"
  )

fig6 <- ggplot2::ggplot(ratio_dose, ggplot2::aes(x = Dose_gL, y = Ratio_moy, fill = Dose_gL)) +
  ggplot2::geom_col(alpha = 0.88, width = 0.55, colour = "grey25", linewidth = 0.4) +
  ggplot2::geom_errorbar(
    ggplot2::aes(ymin = pmax(0, Ratio_moy - Ratio_sd), ymax = Ratio_moy + Ratio_sd),
    width = 0.18, color = "grey20", linewidth = 0.5) +
  ggplot2::geom_text(ggplot2::aes(label = sprintf("%.2f", Ratio_moy), y = Ratio_moy + Ratio_sd + 0.03),
                     family = FONT_MAIN, fontface = "bold", size = 3.3, colour = "#1B2838") +
  ggplot2::scale_fill_manual(values = PALETTE_DOSE, guide = "none") +
  ggplot2::scale_x_discrete(labels = DOSE_LABELS) +
  ggplot2::labs(
    title    = "Figure 6 \u2014 Ratio longueur racine / longueur tige au J21",
    subtitle = "Un ratio decroissant revele une inhibition racinaire plus forte que celle de la tige",
    x = "Concentration saline (g/L)", y = "Ratio racine / tige (mm/mm)") +
  theme_salinite
save_fig("Fig6_ratio_racine_tige", fig6)

# ============================================================
# Fig 7. Indice de tolerance au sel (STI) vs CE
# ============================================================
sti_data <- desc_germ %>%
  dplyr::select(Dose_gL, STI_pct, CE_theorique_dSm) %>%
  dplyr::mutate(Dose_gL = factor(Dose_gL, levels = NIVEAUX_DOSE))

fig7 <- ggplot2::ggplot(sti_data, ggplot2::aes(x = CE_theorique_dSm, y = STI_pct, fill = Dose_gL)) +
  ggplot2::geom_line(ggplot2::aes(group = 1), color = "grey60", linewidth = 1) +
  ggplot2::geom_point(size = 5, shape = 21, stroke = 1.5, color = "grey20") +
  ggplot2::geom_text(ggplot2::aes(label = paste0(Dose_gL, " g/L")),
                     family = FONT_MAIN, vjust = -1.4, size = 3.5, fontface = "bold") +
  ggplot2::scale_fill_manual(values = PALETTE_DOSE, guide = "none") +
  ggplot2::scale_y_continuous(limits = c(-5, 120), labels = scales::percent_format(scale = 1)) +
  ggplot2::geom_hline(yintercept = 50, linetype = "dashed", color = "#EF4444", linewidth = 0.7) +
  ggplot2::annotate("text", x = 45, y = 54, family = FONT_MAIN,
                    label = "Seuil 50 % de tolerance", color = "#EF4444", size = 3.2, hjust = 0) +
  ggplot2::labs(
    title    = "Figure 7 \u2014 Indice de tolerance au sel (STI) en fonction de la CE",
    subtitle = "STI = (Taux germination traite / Taux germination temoin) \u00d7 100",
    x = "Conductivite electrique theorique (dS/m)", y = "Indice de tolerance au sel (%)") +
  theme_salinite
save_fig("Fig7_indice_tolerance_sel", fig7)

# ============================================================
# Fig 8. Regression dose-reponse (germination) + densite marginale
# ============================================================
pred_df <- data.frame(Dose_num = seq(0, 45, by = 0.5))
pred_df$Germ_lin  <- predict(reg_germ,   newdata = pred_df)
pred_df$Germ_quad <- predict(reg_germ_q, newdata = pred_df)

r2_lin  <- round(summary(reg_germ)$r.squared,   3)
r2_quad <- round(summary(reg_germ_q)$r.squared,  3)
p_lin   <- round(coef(summary(reg_germ))[2, 4],  4)

p_main8 <- ggplot2::ggplot(data_j21, ggplot2::aes(x = Dose_num, y = Taux_Germination_J21)) +
  ggplot2::geom_point(ggplot2::aes(fill = Dose_gL), size = 3.3, shape = 21,
                      colour = "grey25", stroke = 1) +
  ggplot2::geom_line(data = pred_df, ggplot2::aes(x = Dose_num, y = Germ_lin),
                     colour = "#0EA5E9", linewidth = 1.1) +
  ggplot2::geom_line(data = pred_df, ggplot2::aes(x = Dose_num, y = Germ_quad),
                     colour = "#EF4444", linewidth = 1.1, linetype = "dashed") +
  ggplot2::scale_fill_manual(values = PALETTE_DOSE, name = "Dose", labels = DOSE_LABELS) +
  ggplot2::scale_y_continuous(limits = c(-5, 115), labels = scales::percent_format(scale = 1)) +
  ggplot2::annotate("text", x = 16, y = 108, family = FONT_MAIN, fontface = "bold",
                    label = paste0("Lineaire : R\u00b2 = ", r2_lin, "  (p = ", p_lin, ")"),
                    colour = "#0EA5E9", size = 3.3, hjust = 0) +
  ggplot2::annotate("text", x = 16, y = 98, family = FONT_MAIN, fontface = "bold",
                    label = paste0("Quadratique : R\u00b2 = ", r2_quad),
                    colour = "#EF4444", size = 3.3, hjust = 0) +
  ggplot2::labs(
    title    = "Figure 8 \u2014 Regression dose-reponse : germination vs concentration saline",
    subtitle = "Bleu = modele lineaire  |  Rouge pointille = modele quadratique",
    x = "Concentration saline (g/L)", y = "Taux de germination (%)") +
  theme_salinite

p_right8 <- ggplot2::ggplot(data_j21, ggplot2::aes(x = Taux_Germination_J21, fill = Dose_gL)) +
  ggplot2::geom_density(alpha = 0.55, colour = NA) +
  ggplot2::coord_flip() +
  ggplot2::scale_x_continuous(limits = c(-5, 115)) +
  ggplot2::scale_fill_manual(values = PALETTE_DOSE, guide = "none") +
  ggplot2::theme_void()

fig8 <- (p_main8 + p_right8 +
           patchwork::plot_layout(widths = c(5, 1.1), guides = "collect")) &
  ggplot2::theme(legend.position = "bottom", text = ggplot2::element_text(family = FONT_MAIN))
save_fig("Fig8_regression_dose_reponse", fig8, w = 22, h = 13)

# ============================================================
# Fig 9. Matrice de correlation (corrplot, degrade orange <-> bleu ciel)
# ============================================================
fig9_path <- file.path(OUTPUT_DIR, "figures", "Fig9_matrice_correlation.png")
grDevices::png(fig9_path, width = 18, height = 16, units = "cm", res = 300, bg = "#FBFAF6")
showtext::showtext_begin()
par(family = FONT_MAIN)
corrplot::corrplot(
  mat_corr,
  method      = "ellipse",
  type        = "upper",
  order       = "hclust",
  col         = grDevices::colorRampPalette(c("#FB923C", "white", "#0EA5E9"))(200),
  addCoef.col = "grey20",
  number.cex  = 0.70,
  tl.col      = "#1B2838",
  tl.srt      = 45,
  tl.cex      = 0.80,
  p.mat       = mat_pval,
  sig.level   = 0.05,
  insig       = "blank",
  title       = paste0("Figure 9 \u2014 Matrice de correlation de Pearson (\u03b1 = 0,05)\n",
                       "Cellules vides : correlation non significative"),
  mar         = c(0, 0, 3, 0)
)
showtext::showtext_end()
grDevices::dev.off()
message("  \u2713 ", fig9_path)

# ============================================================
# Fig 10. Panel multi-variables (A: tige, B: racine, C: feuilles, D: ratio)
# ============================================================
panel_theme_extra <- ggplot2::theme(
  axis.text.x = ggplot2::element_text(angle = 30, hjust = 1),
  plot.title  = ggplot2::element_text(size = 11)
)

p_tige_p <- box_stress(data_tige_ok, "Longueur_Tige_mm", cld_tige, "Tige (mm)",
                       "(A) Longueur de tige", NULL, ymax_tige * 1.12) + panel_theme_extra
p_rac_p  <- box_stress(data_racine_ok, "Longueur_Racine_mm", cld_racine, "Racine (mm)",
                       "(B) Longueur de racine", NULL, ymax_racine * 1.12) + panel_theme_extra
p_feui_p <- box_stress(data_j21, "Nb_Feuilles", cld_feui, "Nb feuilles",
                       "(C) Nombre de feuilles", NULL, ymax_feui + 0.7) + panel_theme_extra

p_ratio_p <- ggplot2::ggplot(ratio_dose, ggplot2::aes(x = Dose_gL, y = Ratio_moy, fill = Dose_gL)) +
  ggplot2::geom_col(alpha = 0.88, width = 0.55, colour = "grey25") +
  ggplot2::geom_errorbar(ggplot2::aes(ymin = pmax(0, Ratio_moy - Ratio_sd), ymax = Ratio_moy + Ratio_sd),
                         width = 0.18) +
  ggplot2::scale_fill_manual(values = PALETTE_DOSE, guide = "none") +
  ggplot2::scale_x_discrete(labels = DOSE_LABELS) +
  ggplot2::labs(x = "Dose (g/L)", y = "Ratio R/T", title = "(D) Ratio racine/tige") +
  theme_salinite + panel_theme_extra

fig10 <- (p_tige_p | p_rac_p) / (p_feui_p | p_ratio_p) +
  patchwork::plot_annotation(
    title = "Figure 10 \u2014 Parametres de croissance au J21 selon la dose saline",
    theme = ggplot2::theme(plot.title = ggplot2::element_text(
      face = "bold", size = 13, hjust = 0.5, family = FONT_MAIN, colour = "#1B2838"))
  )
save_fig("Fig10_panel_croissance", fig10, w = 22, h = 18)

# ============================================================
# Fig 11. Evolution de la longueur de tige dans le temps
# ============================================================
fig11 <- ggplot2::ggplot(
  tige_temps, ggplot2::aes(x = Jour, y = Moy_tige, color = Dose_gL, group = Dose_gL)) +
  ggplot2::geom_ribbon(
    ggplot2::aes(ymin = pmax(0, Moy_tige - SD_tige), ymax = Moy_tige + SD_tige, fill = Dose_gL),
    alpha = 0.12, color = NA) +
  ggplot2::geom_line(linewidth = 1.2) +
  ggplot2::geom_point(size = 2.4, shape = 21, fill = "white", stroke = 1.1) +
  ggplot2::scale_color_manual(values = PALETTE_DOSE, labels = DOSE_LABELS, name = "Dose") +
  ggplot2::scale_fill_manual( values = PALETTE_DOSE, labels = DOSE_LABELS, name = "Dose") +
  ggplot2::scale_x_continuous(breaks = c(5, 7, 10, 14, 17, 21),
                              labels = c("J5","J7","J10","J14","J17","J21")) +
  ggplot2::labs(
    title    = "Figure 11 \u2014 Evolution de la longueur de tige selon la dose saline",
    subtitle = "Moyenne \u00b1 ET des 3 blocs (germinations uniquement)",
    x = "Jours apres semis", y = "Longueur de tige (mm)") +
  theme_salinite
save_fig("Fig11_evolution_tige", fig11, w = 20, h = 13)

message("\n\u2713 11 figures exportees dans : ", file.path(OUTPUT_DIR, "figures"))

# =============================================================================
# 7.  EXPORT DES TABLEAUX VERS EXCEL
# =============================================================================

cat("\n=== EXPORT DES TABLEAUX EXCEL ===\n")

wb_res <- openxlsx::createWorkbook()

hs_style <- openxlsx::createStyle(
  fontName       = "Arial", fontSize = 11, fontColour = "white",
  fgFill         = "#2E5C3E", textDecoration = "bold",
  halign         = "center", valign = "center", wrapText = TRUE,
  border         = "TopBottomLeftRight", borderColour = "#CCCCCC"
)

ajouter_feuille <- function(wb, nom, df, titre = NULL) {
  openxlsx::addWorksheet(wb, nom)
  startRow <- if (!is.null(titre)) 3L else 1L
  if (!is.null(titre)) {
    openxlsx::writeData(wb, nom, titre, startRow = 1, startCol = 1)
    openxlsx::addStyle(wb, nom,
                       openxlsx::createStyle(fontName = "Arial", fontSize = 13,
                                             textDecoration = "bold", fontColour = "#1F3D2B"),
                       rows = 1, cols = 1)
  }
  openxlsx::writeData(wb, nom, df, startRow = startRow, startCol = 1,
                      headerStyle = hs_style,
                      borders = "all", borderColour = "#CCCCCC")
  openxlsx::setColWidths(wb, nom, cols = seq_len(ncol(df)), widths = "auto")
  openxlsx::freezePane(wb, nom, firstActiveRow = startRow + 1L)
}

# -- T1 : Statistiques descriptives -----------------------------------------
ajouter_feuille(wb_res, "T1_Stats_descriptives", as.data.frame(desc_germ),
                "Tableau 1 \u2014 Statistiques descriptives J21 par dose (n = 3 blocs)")

# -- T2 : Resultats ANOVA ---------------------------------------------------
get_anova_row <- function(aov_obj, nom_var) {
  data.frame(
    Variable    = nom_var,
    F_value     = round(aov_obj[1, "F value"], 3),
    Df_num      = aov_obj[1, "NumDF"],
    Df_den      = round(aov_obj[1, "DenDF"], 1),
    p_value     = round(aov_obj[1, "Pr(>F)"], 4),
    Signif      = dplyr::case_when(
      aov_obj[1, "Pr(>F)"] < 0.001 ~ "***",
      aov_obj[1, "Pr(>F)"] < 0.01  ~ "**",
      aov_obj[1, "Pr(>F)"] < 0.05  ~ "*",
      TRUE ~ "ns"
    )
  )
}

anova_resume <- dplyr::bind_rows(
  get_anova_row(aov_germ,   "Taux de germination (%)"),
  get_anova_row(aov_tige,   "Longueur de tige (mm)"),
  get_anova_row(aov_racine, "Longueur de racine (mm)"),
  get_anova_row(aov_feui,   "Nombre de feuilles"),
  get_anova_row(aov_ratio,  "Ratio racine/tige")
)
ajouter_feuille(wb_res, "T2_ANOVA", anova_resume,
                "Tableau 2 \u2014 ANOVA DBCR (effet fixe : Dose | effet aleatoire : Bloc)")

# -- T3 : Groupes homogenes Tukey CLD ---------------------------------------
mk_cld_df <- function(cld_df, nom_var) {
  cld_df %>%
    dplyr::transmute(
      Variable        = nom_var,
      Dose_gL         = as.character(Dose_gL),
      Moyenne         = round(emmean, 2),
      SE              = round(SE, 2),
      IC_inf          = round(lower.CL, 2),
      IC_sup          = round(upper.CL, 2),
      Groupe_homogene = trimws(.group)
    )
}

tukey_resume <- dplyr::bind_rows(
  mk_cld_df(cld_germ,   "Germination (%)"),
  mk_cld_df(cld_tige,   "Longueur tige (mm)"),
  mk_cld_df(cld_racine, "Longueur racine (mm)"),
  mk_cld_df(cld_feui,   "Nb feuilles")
)
ajouter_feuille(wb_res, "T3_Tukey_CLD", tukey_resume,
                "Tableau 3 \u2014 Comparaisons multiples Tukey HSD (\u03b1 = 0,05) et groupes homogenes")

# -- T4 : Regression --------------------------------------------------------
mk_reg_row <- function(mod, nom_var) {
  s <- summary(mod)
  data.frame(
    Variable       = nom_var,
    Intercept      = round(coef(mod)[1], 3),
    Pente          = round(coef(mod)[2], 3),
    R2             = round(s$r.squared, 4),
    R2_adj         = round(s$adj.r.squared, 4),
    F_global       = round(s$fstatistic[1], 3),
    p_pente        = round(coef(s)[2, 4], 4),
    Equation       = paste0("y = ", round(coef(mod)[1], 2),
                            ifelse(coef(mod)[2] >= 0, " + ", " - "),
                            abs(round(coef(mod)[2], 3)), "x")
  )
}

reg_resume <- dplyr::bind_rows(
  mk_reg_row(reg_germ,   "Germination (%)"),
  mk_reg_row(reg_tige,   "Longueur tige (mm)"),
  mk_reg_row(reg_racine, "Longueur racine (mm)")
)
ajouter_feuille(wb_res, "T4_Regression", reg_resume,
                "Tableau 4 \u2014 Parametres des regressions lineaires dose-reponse")

# -- T5 : Matrice de correlation --------------------------------------------
mat_corr_df <- as.data.frame(round(mat_corr, 3))
mat_corr_df <- cbind(Variable = rownames(mat_corr_df), mat_corr_df)
rownames(mat_corr_df) <- NULL
ajouter_feuille(wb_res, "T5_Correlation", mat_corr_df,
                "Tableau 5 \u2014 Matrice de correlation de Pearson")

# -- T6 : Donnees brutes J21 ------------------------------------------------
data_j21_export <- data_j21 %>%
  dplyr::select(Bloc, Dose_gL, Pot_ID,
                Taux_Germination_J21, Longueur_Tige_mm,
                Longueur_Racine_mm, Nb_Feuilles,
                Ratio_Racine_Tige, Surface_Foliaire_cm2,
                CE_dSm, Source)
ajouter_feuille(wb_res, "T6_Donnees_J21", as.data.frame(data_j21_export),
                "Tableau 6 \u2014 Donnees J21 (OBS = observe | EST = estime par interpolation)")

# -- Sauvegarde -------------------------------------------------------------
fichier_res <- file.path(OUTPUT_DIR, "tableaux",
                         "Resultats_analyse_germination_haricot.xlsx")
openxlsx::saveWorkbook(wb_res, fichier_res, overwrite = TRUE)
message("\u2713 Classeur exporte : ", fichier_res)

# =============================================================================
# 8.  RESUME CONSOLE
# =============================================================================

cat("\n")
cat("================================================================\n")
cat("  RESUME — Germination haricot / stress salin (DBCR, J21)\n")
cat("================================================================\n")
cat(sprintf("  Pots analyses  : %d  (3 blocs x 5 doses x 1 observation)\n",
            nrow(data_j21)))
cat("  Graines/pot    : 9\n")
cat("  Duree          : 21 jours (21 juin - 12 juillet 2025)\n\n")
cat("  Taux germination moyen (%) \u00b1 SD  —  STI (%) :\n")
for (i in seq_len(nrow(desc_germ))) {
  cat(sprintf("    %-5s g/L : %5.1f%% \u00b1 %4.1f%%   STI = %5.1f%%\n",
              as.character(desc_germ$Dose_gL[i]),
              desc_germ$Germ_Moy_pct[i],
              desc_germ$Germ_SD[i],
              desc_germ$STI_pct[i]))
}
cat("\n  Tige moyenne (mm) \u00b1 SD au J21 :\n")
for (i in seq_len(nrow(desc_germ))) {
  cat(sprintf("    %-5s g/L : %6.1f \u00b1 %4.1f mm\n",
              as.character(desc_germ$Dose_gL[i]),
              desc_germ$Tige_Moy_mm[i],
              desc_germ$Tige_SD_mm[i]))
}
cat("\n  Outputs :\n")
cat("    figures/  -> 11 figures PNG 300 dpi (design v3 : palette unique + Roboto)\n")
cat("    tableaux/ -> Resultats_analyse_germination_haricot.xlsx (6 onglets)\n")
cat("================================================================\n\n")

message("\u2713 Analyse complete terminee. Resultats dans : ", OUTPUT_DIR)