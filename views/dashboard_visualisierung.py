# views/dashboard_visualisierung.py
import os
import logging
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # Nicht-interaktives Backend verwenden
from typing import Dict, Any

# Logger konfigurieren
logger = logging.getLogger(__name__)

class DashboardVisualisierung:
    """
    Klasse für die grafische Darstellung von Daten.

    Diese Klasse ist verantwortlich für die Erstellung verschiedener
    Visualisierungen wie Balkendiagramme, Liniendiagramme und Fortschrittsbalken,
    die im Dashboard angezeigt werden. Sie nutzt matplotlib für die Generierung
    der Grafiken und speichert diese als Bilddateien.
    """

    def __init__(self, ausgabe_pfad: str = "grafiken"):
        """
        Initialisiert ein DashboardVisualisierung-Objekt mit dem angegebenen Ausgabepfad.

        Parameter:
            ausgabe_pfad: Verzeichnis zum Speichern der Grafiken (Standard: "grafiken")
        """
        self.ausgabe_pfad = ausgabe_pfad

        # Stelle sicher, dass das Verzeichnis existiert
        if not os.path.exists(self.ausgabe_pfad):
            os.makedirs(self.ausgabe_pfad)

    def erstelle_balkendiagramm(self,
                                dict_data: Dict[str, float],
                                titel: str,
                                x_label: str,
                                y_label: str,
                                dateiname: str) -> str:
        """
        Erstellt ein Balkendiagramm aus den übergebenen Daten.

        Diese Methode generiert ein anpassbares Balkendiagramm mit
        beschrifteten Achsen und Werten über den Balken.

        Parameter:
            dict_data: Dictionary mit Daten für das Diagramm (Schlüssel: Kategorien, Werte: Datenpunkte)
            titel: Titel des Diagramms
            x_label: Beschriftung der x-Achse
            y_label: Beschriftung der y-Achse
            dateiname: Dateiname zum Speichern des Diagramms (ohne Dateiendung)

        Rückgabe:
            Pfad zur gespeicherten Grafik
        """
        try:
            # Lösche alle vorhandenen Figuren
            plt.clf()

            # Erstelle Figur
            fig, ax = plt.subplots(figsize=(10, 6))

            # Erstelle Balkendiagramm
            bars = ax.bar(list(dict_data.keys()), list(dict_data.values()))

            # Füge Beschriftungen und Titel hinzu
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(titel)

            # Füge, für bessere Lesbarkeit, Werte über den Balken hinzu
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.1f}', ha='center', va='bottom')

            # Setze y-Achse so, dass sie bei 0 beginnt
            ax.set_ylim(bottom=0)

            # Passe Layout an
            plt.tight_layout()

            # Speichere die Figur
            file_path = os.path.join(self.ausgabe_pfad, f"{dateiname}.png")
            plt.savefig(file_path)
            plt.close(fig)  # Schließe die Figur, um Ressourcen freizugeben

            return file_path
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Balkendiagramms: {e}", exc_info=True)
            print(f"Fehler beim Erstellen des Balkendiagramms: {e}")
            return ""

    def erstelle_liniendiagramm(self,
                                dict_data: Dict[str, float],
                                titel: str,
                                x_label: str,
                                y_label: str,
                                dateiname: str) -> str:
        """
        Erstellt ein Liniendiagramm aus den übergebenen Daten.

        Diese Methode generiert ein anpassbares Liniendiagramm mit Markern
        an den Datenpunkten und Wertbeschriftungen.

        Parameter:
            dict_data: Dictionary mit Daten für das Diagramm (Schlüssel: x-Werte, Werte: y-Werte)
            titel: Titel des Diagramms
            x_label: Beschriftung der x-Achse
            y_label: Beschriftung der y-Achse
            dateiname: Dateiname zum Speichern des Diagramms (ohne Dateiendung)

        Rückgabe:
            Pfad zur gespeicherten Grafik
        """
        try:
            # Lösche alle vorhandenen Figuren
            plt.clf()

            # Erstelle Figur
            fig, ax = plt.subplots(figsize=(10, 6))

            # Sortiere Schlüssel, falls sie Zahlen sind, für korrekte Reihenfolge
            try:
                keys = sorted([int(k) for k in dict_data.keys()])
                keys = [str(k) for k in keys]
                values = [dict_data[str(k)] for k in keys]
            except (ValueError, TypeError):
                # Wenn Schlüssel nicht in Ganzzahlen konvertiert werden können, verwende sie unverändert
                keys = list(dict_data.keys())
                values = list(dict_data.values())

            # Erstelle Liniendiagramm
            ax.plot(keys, values, marker='o', linestyle='-')

            # Füge Beschriftungen und Titel hinzu
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(titel)

            # Füge, für bessere Lesbarkeit, Werte an den Datenpunkten hinzu
            for i, value in enumerate(values):
                ax.text(i, value, f'{value:.1f}', ha='center', va='bottom')

            # Passe Layout an
            plt.tight_layout()

            # Speichere die Figur
            file_path = os.path.join(self.ausgabe_pfad, f"{dateiname}.png")
            plt.savefig(file_path)
            plt.close(fig)  # Schließe die Figur, um Ressourcen freizugeben

            return file_path
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Liniendiagramms: {e}", exc_info=True)
            print(f"Fehler beim Erstellen des Liniendiagramms: {e}")
            return ""

    def erstelle_fortschrittsbalken(self,
                                    wert: float,
                                    gesamt: float,
                                    titel: str,
                                    dateiname: str) -> str:
        """
        Erstellt einen horizontalen Fortschrittsbalken.

        Diese Methode visualisiert einen Fortschrittswert im Verhältnis zu einem
        Gesamtwert, was besonders nützlich für die Anzeige des ECTS-Fortschritts ist.

        Parameter:
            wert: Aktueller Wert (z.B. absolvierte ECTS)
            gesamt: Gesamtwert (z.B. benötigte ECTS für den Abschluss)
            titel: Titel des Diagramms
            dateiname: Dateiname zum Speichern des Diagramms (ohne Dateiendung)

        Rückgabe:
            Pfad zur gespeicherten Grafik
        """
        try:
            # Lösche alle vorhandenen Figuren
            plt.clf()

            # Erstelle Figur mit geringer Höhe für einen ästhetischen Fortschrittsbalken
            fig, ax = plt.subplots(figsize=(10, 2))

            # Berechne Prozentsatz
            prozent = (wert / gesamt) * 100 if gesamt > 0 else 0

            # Erstelle Fortschrittsbalken
            ax.barh(0, prozent, height=0.5, color='blue')  # Blauer Balken für den Fortschritt
            ax.barh(0, 100, height=0.5, color='lightgray', alpha=0.5)  # Grauer Hintergrund für den Gesamtwert

            # Füge Text hinzu (mittig im Balken)
            ax.text(50, 0, f'{wert}/{gesamt} ({prozent:.1f}%)',
                    ha='center', va='center', color='black')

            # Entferne Achsen und Rahmen für eine saubere Darstellung
            ax.set_yticks([])
            ax.set_xticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            # Füge Titel hinzu
            ax.set_title(titel)

            # Passe Layout an
            plt.tight_layout()

            # Speichere die Figur
            file_path = os.path.join(self.ausgabe_pfad, f"{dateiname}.png")
            plt.savefig(file_path)
            plt.close(fig)  # Schließe die Figur, um Ressourcen freizugeben

            return file_path
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Fortschrittsbalkens: {e}", exc_info=True)
            print(f"Fehler beim Erstellen des Fortschrittsbalkens: {e}")
            return ""

    def erstelle_notenuebersicht(self,
                                 noten_data: Dict[str, Any],
                                 ziel_note: float,
                                 dateiname: str) -> str:
        """
        Erstellt eine Übersicht der Noten mit zwei Teildiagrammen.

        Diese Methode generiert eine zusammengesetzte Grafik mit zwei Teilbereichen:
        1. Aktueller Notendurchschnitt im Vergleich zum Zielwert
        2. Verteilung der Noten in einem Histogramm

        Parameter:
            noten_data: Dictionary mit Noteninformationen
                        ("aktuell": aktueller Durchschnitt, "verteilung": Häufigkeit der Noten)
            ziel_note: Angestrebter Notendurchschnitt
            dateiname: Dateiname zum Speichern des Diagramms (ohne Dateiendung)

        Rückgabe:
            Pfad zur gespeicherten Grafik
        """
        try:
            # Lösche alle vorhandenen Figuren
            plt.clf()

            # Erstelle Figur mit 2 Teildiagrammen
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Linkes Teildiagramm: Aktuell vs. Ziel
            current = noten_data.get("aktuell", 0.0)

            bars1 = ax1.bar(["Aktuell", "Ziel"], [current, ziel_note])
            ax1.set_ylim(0, 5)  # Unsere Notenskala geht von 1.0 bis 5.0
            ax1.invert_yaxis()  # Invertiere y-Achse, da in unserem System kleinere Noten besser sind
            ax1.set_title("Notendurchschnitt: Aktuell vs. Ziel")

            # Füge Werte über den Balken hinzu
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{height:.1f}', ha='center', va='bottom')

            # Rechtes Teildiagramm: Notenverteilung
            verteilung = noten_data.get("verteilung", {})

            if verteilung:
                # Sortiere Schlüssel nach Notenwert für bessere Lesbarkeit
                sorted_keys = sorted(verteilung.keys(), key=lambda x: float(x))

                bars2 = ax2.bar(sorted_keys, [verteilung[k] for k in sorted_keys])
                ax2.set_title("Notenverteilung")
                ax2.set_xlabel("Note")
                ax2.set_ylabel("Anzahl")

                # Füge Werte über den Balken hinzu
                for bar in bars2:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width() / 2., height,
                             f'{height}', ha='center', va='bottom')
            else:
                ax2.text(0.5, 0.5, "Keine Notendaten verfügbar", ha='center', va='center')
                ax2.set_title("Notenverteilung")

            # Passe Layout an
            plt.tight_layout()

            # Speichere die Figur
            file_path = os.path.join(self.ausgabe_pfad, f"{dateiname}.png")
            plt.savefig(file_path)
            plt.close(fig)  # Schließe die Figur, um Ressourcen freizugeben

            return file_path
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Notenübersicht: {e}", exc_info=True)
            print(f"Fehler beim Erstellen der Notenübersicht: {e}")
            return ""

    def speichere_grafik(self, plt_figure, dateiname: str) -> str:
        """
        Speichert eine matplotlib-Figur.

        Diese Methode ist ein Hilfswerkzeug, um eine bereits erstellte matplotlib-Figur
        unter dem angegebenen Namen zu speichern.

        Parameter:
            plt_figure: Die zu speichernde matplotlib-Figur
            dateiname: Dateiname zum Speichern der Figur (ohne Dateiendung)

        Rückgabe:
            Pfad zur gespeicherten Figur
        """
        try:
            file_path = os.path.join(self.ausgabe_pfad, f"{dateiname}.png")
            plt_figure.savefig(file_path)
            plt.close(plt_figure)  # Schließe die Figur, um Ressourcen freizugeben
            return file_path
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Grafik: {e}", exc_info=True)
            print(f"Fehler beim Speichern der Grafik: {e}")
            return ""