import pygame as pg
from .configs import GFX


def adjust_gif(num_frames, frame_format, subfolder, scale=True, fps=12):
    """
    formatar o GIF para display

    num_frames   → quantidade de frames (inclusive o último, COMEÇANDO DO 0)
    frame_format → string de formato, ex: "frame_{}", onde {} indica o lugar dos números
    subfolder    → chave dentro de GFX onde estão os frames
    scale        → igual ao das imagens estáticas (bool ou float)
    fps          → frames por segundo
    """

    frames = [GFX[subfolder][frame_format.format(
        i)] for i in range(num_frames)]
    return {"image": frames, "scale": scale, "fps": fps}


CONTENT_MAP = {

    "Euclide": {
        # FASE 3
        5: {2: {"image": GFX["dialogs"]["maquete"], "scale": True},
            3: {"image": GFX["dialogs"]["projetil"], "scale": True},
            4: adjust_gif(75, "frame_{}", "circuit_gif", scale=True, fps=15),
            5: adjust_gif(11, "frame_{}", "ai_gif", scale=True, fps=1)
            },
        7: {5: {"image": GFX["dialogs"]["cooking"], "scale": True},
            },

        # FASE 4
        9: {19: {"image": GFX["dialogs"]["sensor_temp"], "scale": True}, },
        10: {4: {"image": GFX["dialogs"]["filtro"], "scale": True},
             5: adjust_gif(126, "frame_{}", "filter_gif", scale=True, fps=13),
             6: {"image": GFX["dialogs"]["pc_filter"], "scale": True},
             7: {"image": GFX["dialogs"]["espuma"], "scale": True},
             9: {"image": GFX["dialogs"]["filtro_agua"], "scale": True},
             },
        12: {6: adjust_gif(121, "newton_{}", "newton_gif", scale=True, fps=24),
             20: {"image": GFX["dialogs"]["circ_rc"], "scale": True}},
        13: {4: {"image": GFX["dialogs"]["tb"], "scale": True}},

        # FASE 5
        15: {3: {"image": GFX["dialogs"]["bicicleta"], "scale": True},
             4: {"image": GFX["dialogs"]["bicicleta_partes"], "scale": True},
             5: {"image": GFX["dialogs"]["bicicleta_cad"], "scale": True},
             },
        16: {7: {"image": GFX["dialogs"]["rn"], "scale": True},
             12: {"image": GFX["dialogs"]["narmax"], "scale": True},
             13: {"image": GFX["dialogs"]["narmax"], "scale": True},
             15: {"image": GFX["dialogs"]["ex_atraso"], "scale": False},
             16: {"image": GFX["dialogs"]["ex_atraso_2"], "scale": True},
             17: {"image": GFX["dialogs"]["ex_atraso_2"], "scale": True},
             18: {"image": GFX["dialogs"]["ex_atraso_2"], "scale": True},
             },
        17: {1: {"image": GFX["dialogs"]["narmax"], "scale": True},
             2: {"image": GFX["dialogs"]["narmax"], "scale": True},
             4: {"image": GFX["dialogs"]["ex_l"], "scale": False},
             5: {"image": GFX["dialogs"]["ex_l"], "scale": False},
             6: {"image": GFX["dialogs"]["narmax"], "scale": True},
             8: {"image": GFX["dialogs"]["ajuste"], "scale": True},
             9: {"image": GFX["dialogs"]["ajuste"], "scale": True},
             18: {"image": GFX["dialogs"]["agrup_1"], "scale": True},
             19: {"image": GFX["dialogs"]["agrup_1"], "scale": True},
             21: {"image": GFX["dialogs"]["agrup_2"], "scale": True},
             24: {"image": GFX["dialogs"]["akaike"], "scale": True},
             },
        18: {9: {"image": GFX["dialogs"]["ex_atraso"], "scale": False},
             13: {"image": GFX["dialogs"]["ex_narmax"], "scale": True},
             14: {"image": GFX["dialogs"]["ex_narmax"], "scale": True},
             15: {"image": GFX["dialogs"]["ex_narmax"], "scale": True},
             16: {"image": GFX["dialogs"]["ex_narmax"], "scale": True},
             17: {"image": GFX["dialogs"]["ex_narmax"], "scale": True},
             18: {"image": GFX["dialogs"]["eq_residuos"], "scale": True},
             25: {"image": GFX["dialogs"]["dados_amostrados"], "scale": True},
             26: {"image": GFX["dialogs"]["dados_amostrados_ls"], "scale": True},
             27: {"image": GFX["dialogs"]["dados_amostrados_mini"], "scale": True},

             },

        19: {6: {"image": GFX["dialogs"]["pintor"], "scale": True},
             7: {"image": GFX["dialogs"]["pintor"], "scale": True},
             9: {"image": GFX["dialogs"]["fit_model"], "scale": True},
             },
        20: {4: {"image": GFX["dialogs"]["e2"], "scale": True},
             5: {"image": GFX["dialogs"]["e2"], "scale": True},
             6: {"image": GFX["dialogs"]["x1e"], "scale": True},
             7: {"image": GFX["dialogs"]["x1e"], "scale": True},
             8: {"image": GFX["dialogs"]["x1e"], "scale": True}}
    }
}
