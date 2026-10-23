from backend.app.core.database import engine, Base, SessionLocal
from backend.app.models.entities import Nivel, Gesto, Licao, NivelDificuldade, TipoExercicio

def seed_database():
    print("Criando tabelas na base de dados...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Verifica se já existem dados para evitar duplicação
        if db.query(Nivel).first():
            print("[INFO] A base de dados já possui dados iniciais. Nenhuma alteração feita.")
            return

        print("Populando dados pedagógicos da plataforma Sinaliza...")

        # 1. Criação dos Níveis Curriculares (Figma: Primeiros Sinais)
        nivel_iniciante = Nivel(
            slug="primeiros-sinais-vogais",
            titulo="Vogais em LIBRAS",
            dificuldade=NivelDificuldade.INICIANTE,
            descricao="Conheça A, E, I, O e U com demonstrações em vídeo e exercícios leves para praticar.",
            ordem=1,
            icone_tag="AE"
        )
        
        nivel_alfabeto = Nivel(
            slug="alfabeto-completo",
            titulo="Alfabeto: de A a Z",
            dificuldade=NivelDificuldade.INICIANTE,
            descricao="Explore o alfabeto manual e a datilologia para soletrar palavras, letra por letra.",
            ordem=2,
            icone_tag="BC"
        )

        db.add_all([nivel_iniciante, nivel_alfabeto])
        db.flush()

        # 2. Gestos Alvo (Sincronizados com os rótulos do YOLO)
        gesto_a = Gesto(nome="Vogal A", rotulo_yolo="A", categoria="vogal")
        gesto_e = Gesto(nome="Vogal E", rotulo_yolo="E", categoria="vogal")
        gesto_i = Gesto(nome="Vogal I", rotulo_yolo="I", categoria="vogal")
        gesto_o = Gesto(nome="Vogal O", rotulo_yolo="O", categoria="vogal")
        gesto_u = Gesto(nome="Vogal U", rotulo_yolo="U", categoria="vogal")

        db.add_all([gesto_a, gesto_e, gesto_i, gesto_o, gesto_u])
        db.flush()

        # 3. Lições da Trilha Vogais (Telas 2 e 5 do Figma)
        licoes = [
            Licao(
                nivel_id=nivel_iniciante.id,
                gesto_alvo_id=gesto_a.id,
                titulo="Conheça a vogal A",
                subtitulo="Vídeo e primeiro contato com a vogal",
                tipo=TipoExercicio.OBSERVACAO,
                ordem=1,
                duracao_minutos=3,
                video_demonstracao_url="/assets/videos/vogal_a.mp4"
            ),
            Licao(
                nivel_id=nivel_iniciante.id,
                gesto_alvo_id=gesto_a.id,
                titulo="Pratique as vogais A e E",
                subtitulo="Observe, repita e reconheça os sinais",
                tipo=TipoExercicio.PRATICA_CAMERA,
                ordem=2,
                duracao_minutos=5
            ),
            Licao(
                nivel_id=nivel_iniciante.id,
                gesto_alvo_id=gesto_e.id,
                titulo="Vogais na prática: Vogal E",
                subtitulo="Observe com atenção e reconheça as vogais A e E.",
                tipo=TipoExercicio.PRATICA_CAMERA,
                ordem=3,
                duracao_minutos=5,
                video_demonstracao_url="/assets/videos/vogal_e.mp4"
            ),
            Licao(
                nivel_id=nivel_iniciante.id,
                gesto_alvo_id=gesto_i.id,
                titulo="A seguir: conheça I, O e U",
                subtitulo="Continuidade das vogais do alfabeto manual",
                tipo=TipoExercicio.PRATICA_CAMERA,
                ordem=4,
                duracao_minutos=6
            ),
            Licao(
                nivel_id=nivel_iniciante.id,
                gesto_alvo_id=None,
                titulo="Revisão geral das vogais",
                subtitulo="Desafio com feedback contínuo do avatar",
                tipo=TipoExercicio.PRATICA_CAMERA,
                ordem=5,
                duracao_minutos=6
            )
        ]

        db.add_all(licoes)
        db.commit()
        print("[OK] Base de dados inicializada com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"[ERRO] Falha ao povoar a base de dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()