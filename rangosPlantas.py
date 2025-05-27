Rangos_ideales = {
  "Plantas": {
    "Lechuga_orejona": {
      "temp": {
        "bueno": { "min": 18, "max": 22 },
        "regular_1": { "min": 15, "max": 17 },
        "regular_2": { "min": 23, "max": 25 },
        "malo": { "min": 0, "max": 14, "extra_max": 26 } 
      },
      "CE": { # en mS/cm
        "bueno": { "min": 1.2, "max": 1.8 },
        "regular": [0.9, 1.0, 1.1, 1.9, 2.0, 2.1],
        "malo": { "min": 0.0, "max": 0.8, "extra_max": 2.2 }
      },
      "pH": {
        "bueno": { "min": 5.5, "max": 6.5 },
        "regular": [5.2, 5.3, 5.4, 6.6, 6.7, 6.8], 
        "malo": { "min": 0.0, "max": 5.1, "extra_max": 6.9 } 
      }
    },
    "Espinaca": {
      "temp": { 
        "bueno": { "min": 16, "max": 22 }, 
        "regular_1": { "min": 13, "max": 15 },
        "regular_2": { "min": 23, "max": 25 },
        "malo": { "min": 0, "max": 12, "extra_max": 26 }
      },
      "CE": { # en mS/cm
        "bueno": { "min": 1.8, "max": 2.5 }, 
        "regular": [1.5, 1.6, 1.7, 2.6, 2.7, 2.8],
        "malo": { "min": 0.0, "max": 1.4, "extra_max": 2.9 }
      },
      "pH": {
        "bueno": { "min": 5.5, "max": 6.5 },
        "regular": [5.2, 5.3, 5.4, 6.6, 6.7, 6.8],
        "malo": { "min": 0.0, "max": 5.1, "extra_max": 6.9 }
      }
    },
    "Cilantro": {
      "temp": { 
        "bueno": { "min": 17, "max": 23 },
        "regular_1": { "min": 12, "max": 16 },
        "regular_2": { "min": 24, "max": 28 },
        "malo": { "min": 0, "max": 11, "extra_max": 29 }
      },
      "CE": { # en mS/cm
        "bueno": { "min": 1.6, "max": 2.2 },
        "regular": [1.3, 1.4, 1.5, 2.3, 2.4, 2.5],
        "malo": { "min": 0.0, "max": 1.2, "extra_max": 2.6 }
      },
      "pH": {
        "bueno": { "min": 5.5, "max": 6.5 },
        "regular": [5.2, 5.3, 5.4, 6.6, 6.7, 6.8],
        "malo": { "min": 0.0, "max": 5.1, "extra_max": 6.9 }
      }
    },
    "Albahaca": {
      "temp": { 
        "bueno": { "min": 22, "max": 28 },
        "regular_1": { "min": 18, "max": 21 },
        "regular_2": { "min": 29, "max": 32 },
        "malo": { "min": 0, "max": 17, "extra_max": 33 }
      },
      "CE": { # en mS/cm
        "bueno": { "min": 1.4, "max": 2.0 },
        "regular": [1.1, 1.2, 1.3, 2.1, 2.2, 2.3],
        "malo": { "min": 0.0, "max": 1.0, "extra_max": 2.4 }
      },
      "pH": {
        "bueno": { "min": 5.5, "max": 6.5 },
        "regular": [5.2, 5.3, 5.4, 6.6, 6.7, 6.8],
        "malo": { "min": 0.0, "max": 5.1, "extra_max": 6.9 }
      }
    }
  }
}