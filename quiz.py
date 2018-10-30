"""Quiz."""


def score_quiz(score):
    """Score the quiz based on answers."""
    O = 8 + score[5] - score[10] + score[15] - score[20] + score[25] - score[30] + score[35] + score[40] + score[45] + score[50]
    C = 14 + score[3] - score[8] + score[13] - score[18] + score[23] - score[28] + score[33] - score[38] + score[43] + score[48]
    E = 20 + score[1] - score[6] + score[11] - score[16] + score[21] - score[26] + score[31] - score[36] + score[41] - score[46]
    A = 14 - score[2] + score[7] - score[12] + score[17] - score[22] + score[27] - score[32] + score[37] + score[42] + score[47]
    N = 38 - score[4] + score[9] - score[14] + score[19] - score[24] - score[29] - score[34] - score[39] - score[44] - score[49]

    return [O, C, E, A, N]

quiz = {
            1: "I am the life of the party.",
            2: "I feel little concern for others.",
            3: "I am always prepared.",
            4: "I get stressed out easily.",
            5: "I have a rich vocabulary.",
            6: "I don't talk a lot.",
            7: "I am interested in people.",
            8: "I leave my belongings around.",
            9: "I am relaxed most of the time.",
            10: "I have difficulty understanding abstract ideas.",
            11: "I feel comfortable around people.",
            12: "I insult people.",
            13: "I pay attention to details.",
            14: "I worry about things.",
            15: "I have a vivid imagination.",
            16: "I like staying in the background.",
            17: "I sympathize with others' feelings.",
            18: "I make a mess of things.",
            19: "I seldom feel blue.",
            20: "I am not interested in abstract ideas.",
            21: "I start conversations.",
            22: "I am not interested in other people's problems.",
            23: "I get chores done right away.",
            24: "I am easily disturbed.",
            25: "I have excellent ideas.",
            26: "I have little to say.",
            27: "I have a soft heart.",
            28: "I often forget to put things back in their proper place.",
            29: "I get upset easily.",
            30: "I do not have a good imagination.",
            31: "I talk to a lot of different people at parties.",
            32: "I am not really interested in others.",
            33: "I like when things are in order.",
            34: "I change my mood a lot.",
            35: "I am quick to understand things.",
            36: "I don't like to draw attention to myself.",
            37: "I take time out for others.",
            38: "I neglect my duties.",
            39: "I have frequent mood swings.",
            40: "I use difficult words.",
            41: "I don't mind being the center of attention.",
            42: "I feel others' emotions.",
            43: "I follow a schedule.",
            44: "I get irritated easily.",
            45: "I spend time reflecting on things.",
            46: "I am quiet around strangers.",
            47: "I make people feel at ease.",
            48: "I am put a lot of effort in my work.",
            49: "I often feel blue.",
            50: "I am full of ideas.",
        }
