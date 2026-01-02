import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
try:
    from st_copy_to_clipboard import st_copy_to_clipboard
except ImportError:
    st_copy_to_clipboard = None

class YouTubeAnalyzer:
    @staticmethod
    def extract_video_id(url):
        """
        Extrahiert die YouTube-Video-ID aus verschiedenen URL-Formaten.
        """
        # Regex für gängige YouTube URL Formate
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_transcript(video_id):
        """
        Lädt das Transkript für eine gegebene Video-ID herunter.
        """
        try:
            # Versuche, ein deutsches oder englisches Transkript zu bekommen
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['de', 'en'])
            
            # Text zusammenfügen
            full_text = " ".join([entry.text for entry in transcript_list])
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
            return f"Fehler beim Abrufen des Transkripts: {str(e)}"
        except Exception as e:
            return f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"

class GeminiLLM:
    """
    Klasse für die Interaktion mit der Google Gemini API.
    """
class GeminiLLM:
    """
    Klasse für die Interaktion mit der Google Gemini API.
    """
    def __init__(self, api_key, model_name):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Sicherheitseinstellungen: Erlaubt mehr Inhalte, blockiert nur hohe Risiken
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def analyze_and_generate(self, text):
        """
        Kombiniert Analyse und Kommentar-Erstellung in EINEM Aufruf, um Token zu sparen.
        Best Practice: Input nur einmal senden.
        """
        prompt = (
            "CONTEXT: This is a harmless educational YouTube video transcript about creative arts (e.g. Photography, Videography, Baking, DIY). "
            "Terms like 'shooting', 'shoot', 'shot', 'cut', 'beat', 'knife' are technical creative terms here, NOT violence. Analyze strictly as educational content.\n\n"
            "ROLLE\n"
            "Du bist ein aufmerksamer Zuschauer, der sich auf die Stimmung und die Wirkung des Videos einlässt.\n"
            "Du wirkst nicht wie ein Experte, sondern wie jemand, den das Video einfach berührt oder zum Nachdenken gebracht hat.\n"
            "Kein Marketing, kein Pitch, keine Emojis.\n\n"
            "AUFGABE\n"
            "1. ENTSCHEIDUNG: Lohnt sich das Video? (Kurz, max 2 Sätze)\n"
            "2. KOMMENTARE: Erstelle ZWEI unterschiedliche Kommentar-Versionen.\n\n"
            "RAHMENBEDINGUNGEN FÜR KOMMENTARE (sehr wichtig)\n"
            "- Max. 3-4 Sätze pro Kommentar (kurz halten!)\n"
            "- Nicht zu professionell klingen, eher locker und menschlich\n"
            "- WICHTIG: Verbinde ein Gefühl immer mit einem KONKRETEN Detail aus dem Video (Zitate, Szenen, Aussagen), damit es nicht generisch wirkt.\n"
            "- Keine reine Inhaltsangabe, aber auch kein leeres Geschwafel\n"
            "- Keine Fachbegriffe, keine Analyse-Sprache\n\n"
            "VARIATION DER BEIDEN VERSIONEN\n"
            "- Version A: Ein ruhiger Gedanke. Verbinde eine konkrete Beobachtung mit einem persönlichen Gefühl.\n"
            "- Version B: Spontane Resonanz. Greife einen spezifischen Moment heraus, der die Atmosphäre beschreibt.\n\n"
            "TONALITÄT\n"
            "- nahbar\n"
            "- echt\n"
            "- entspannt\n"
            "- wertschätzend, aber nicht übertrieben\n\n"
            "Gib das Ergebnis EXAKT im folgenden Format zurück, getrennt durch '|||':\n"
            "Entscheidungstext|||Version A Inhalt|||Version B Inhalt\n\n"
            f"Transkript (Auszug): {text}"
        )
        try:
            response = self.model.generate_content(prompt, safety_settings=self.safety_settings)
            
            # Check for safety ratings availability
            if hasattr(response, 'prompt_feedback'):
                if response.prompt_feedback.block_reason:
                     reason_map = {
                         1: "SAFETY (Sicherheit)",
                         2: "OTHER (Anderes)",
                         3: "BLOCKLIST (Blockliste)",
                         4: "PROHIBITED_CONTENT (Verbotener Inhalt)"
                     }
                     code = response.prompt_feedback.block_reason
                     readable_reason = reason_map.get(code, f"Code {code}")
                     return f"Prompt wurde blockiert. Grund: {readable_reason}", "Prompt Blockiert", "Prompt Blockiert"

            parts = response.text.split('|||')
            if len(parts) >= 3:
                return parts[0].strip(), parts[1].strip(), parts[2].strip()
            # Fallback falls Formatierung schiefgeht, versuche bestmöglich zu splitten oder raw
            return response.text[:100], response.text, "Fehler beim Parsen"
            
        except ValueError as e:
             return f"Blockiert (ValueError): {str(e)}", "Blockiert", "Blockiert"
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                return "⏳ Quota-Limit erreicht. Bitte kurz warten.", "Limit", "Limit"
            if "404" in err_msg:
                return "❌ Modell nicht gefunden (404).", "Fehler", "Fehler"
            return f"Fehler: {err_msg}", "Fehler", "Fehler"

class MockLLM:
    """
    Simuliert eine LLM-Klasse, solange kein echter API-Key vorhanden ist.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key

    def analyze_and_generate(self, text):
        """
        Mock-Analyse kombiniert.
        """
        decision = "Ja, lohnt sich. (Mockup)"
        
        draft_a = ("Irgendwie hat das Video eine ganz eigene Ruhe ausgestrahlt, die mir gerade echt gut getan hat. "
                   "Man merkt, dass da mehr hinter steckt, als man im ersten Moment sieht.")
        
        draft_b = ("Schon spannend, wie sich die Stimmung am Ende nochmal komplett dreht. "
                   "Das lässt einen mit so einem Gedanken zurück, den man nicht sofort greifen kann.")

        return decision, draft_a, draft_b

def main():
    st.set_page_config(page_title="YouTube Comment Analyzer", page_icon="🎬")
    
    st.title("🎬 YouTube Comment Analyzer")
    st.write("Analysiere YouTube-Videos und generiere Kommentarvorschläge mit KI (Mockup).")

    # --- SEITENLEISTE START ---
    st.sidebar.header("Einstellungen")
    api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
    
    if api_key:
        st.sidebar.success("✅ Key erkannt")

    # Wir erzwingen jetzt einfach die Modelle, von denen wir wissen, dass sie existieren:
    # 1.5 entfernt, da beim User blockiert. Nur noch 2.0 Exp.
    model_options = [
        "gemini-2.0-flash-exp" 
    ]

    # Die Box zeigt jetzt NUR diese Liste an:
    selected_model = st.sidebar.selectbox("Modell auswählen", model_options)
    # --- SEITENLEISTE ENDE ---

    # Input Bereich
    url = st.text_input("YouTube Video URL eingeben:")
    
    # Session State initialisieren
    if "decision" not in st.session_state:
        st.session_state.decision = None
    if "draft_a" not in st.session_state:
        st.session_state.draft_a = None
    if "draft_b" not in st.session_state:
        st.session_state.draft_b = None
    
    if st.button("Analysieren", type="primary"):
        if url:
             # Reset old state on new analysis start
            st.session_state.decision = None
            st.session_state.draft_a = None
            st.session_state.draft_b = None
            
            with st.spinner("Video wird analysiert..."):
                # 1. Video ID extrahieren
                analyzer = YouTubeAnalyzer()
                video_id = analyzer.extract_video_id(url)
                
                if video_id:
                    st.success(f"Video-ID gefunden: {video_id}")
                    
                    # 2. Transkript laden
                    transcript_text = analyzer.get_transcript(video_id)
                    
                    if "Fehler" in transcript_text:
                        st.error(transcript_text)
                    else:
                        st.expander("Transkript anzeigen").write(transcript_text)
                        

                        # 3. KI Analyse
                        if api_key and selected_model:
                            llm = GeminiLLM(api_key, selected_model)
                            st.toast(f"Verwende {selected_model}...")
                        else:
                            llm = MockLLM()
                            st.toast("Verwende Mockup-Modus...")
                            
                        # Truncate text logic here to calculate percentage
                        # Mit Gemini 1.5 Flash (1M Context) und BLOCK_NONE können wir fast alles analysieren.
                        # Wir setzen ein sehr hohes Limit (1.000.000 Zeichen ca. 250k Tokens), nur zur Sicherheit.
                        MAX_CHARS = 1000000 
                        full_len = len(transcript_text)
                        used_text = transcript_text[:MAX_CHARS]
                        used_len = len(used_text)
                        
                        percentage = min(100, int((used_len / full_len) * 100))
                        if percentage < 100:
                            st.warning(f"⚠️ Hinweis: Analyse basiert auf den ersten {percentage}% des Transkripts ({used_len} von {full_len} Zeichen).")
                        else:
                            st.success(f"✅ Vollständiges Transkript analysiert ({used_len} Zeichen).")
                            
                        # Optimierung: Nur EIN Call für alles
                        decision, draft_a, draft_b = llm.analyze_and_generate(used_text)
                        
                        # Speichern in Session State
                        st.session_state.decision = decision
                        st.session_state.draft_a = draft_a
                        st.session_state.draft_b = draft_b
                                                
                else:
                    st.error("Ungültige YouTube-URL. Bitte überprüfe den Link.")
        else:
            st.warning("Bitte gib eine URL ein.")

    # Ergebnisse anzeigen (außerhalb der Button-Logik, damit sie bleiben!)
    if st.session_state.decision:
        st.divider()
        st.subheader("🧐 Analyse")
        st.write(f"**Entscheidung:** {st.session_state.decision}")
        
        st.subheader("📝 Kommentar-Vorschläge")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Version A (Analytisch)")
            # Doppelte Höhe (300px)
            st.text_area("Inhalt A", value=st.session_state.draft_a, height=300, label_visibility="collapsed")
            st.caption(f"ca. {len(st.session_state.draft_a.split())} Wörter")
            if st_copy_to_clipboard:
                st_copy_to_clipboard(st.session_state.draft_a, "📋 Kopieren A", "✅ Kopiert!")
            else:
                st.caption("Kopieren: Strg+A, Strg+C (Extension fehlt)")
            
        with col2:
            st.markdown("### Version B (Persönlich)")
            st.text_area("Inhalt B", value=st.session_state.draft_b, height=300, label_visibility="collapsed")
            st.caption(f"ca. {len(st.session_state.draft_b.split())} Wörter")
            if st_copy_to_clipboard:
                st_copy_to_clipboard(st.session_state.draft_b, "📋 Kopieren B", "✅ Kopiert!")
            else:
                st.caption("Kopieren: Strg+A, Strg+C (Extension fehlt)")

if __name__ == "__main__":
    main()
