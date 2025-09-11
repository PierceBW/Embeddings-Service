import numpy as np
import math

class DICE:
    '''
    DICE class turns numbers into their respective DICE embeddings
    
    Since the cosine function decreases monotonically between 0 and pi, simply employ a linear mapping
    to map distances s_n \in [0, |a-b|] to angles \theta \in [0, pi]
    '''
    def __init__(self, d=32, min_bound=0, max_bound=100, norm="l2", seed: int = 13):
        # Minimal POC tweaks:
        # - deterministic basis via fixed seed
        # - keep API mostly the same
        if d < 2:
            raise ValueError("Wrong value for `d`. `d` should be greater than or equal to 2.")
        self.d = int(d)  # By default, we build DICE-2
        self.min_bound = float(min_bound)
        self.max_bound = float(max_bound)
        self.norm = norm  # If "l2", return a unit vector
        self.seed = int(seed)

        rng = np.random.default_rng(self.seed)
        self.M = rng.normal(0.0, 1.0, (self.d, self.d))
        self.Q, self.R = np.linalg.qr(self.M, mode="complete")  # Orthonormal basis Q
    
    def __linear_mapping(self, num):
        """Map value linearly from [min_bound, max_bound] to angle in [0, pi].
        Clamps outside values. Guards against zero range.
        """
        span = self.max_bound - self.min_bound
        if span == 0:
            return 0.0
        t = (float(num) - self.min_bound) / span
        # clamp to [0, 1]
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        theta = t * math.pi
        return theta
    
    def make_dice(self, num):
        r = 1.0
        theta = self.__linear_mapping(num)
        if self.d == 2:
            # DICE-2
            polar_coord = np.array([r * math.cos(theta), r * math.sin(theta)], dtype=np.float32)
        elif self.d > 2:
            # DICE-D
            polar_coord = np.array([
                (math.sin(theta) ** (dim - 1)) * math.cos(theta) if dim < self.d else (math.sin(theta) ** (self.d))
                for dim in range(1, self.d + 1)
            ], dtype=np.float32)
        else:
            # Guarded in __init__, but keep for safety
            raise ValueError("Wrong value for `d`. `d` should be greater than or equal to 2.")

        dice = np.dot(self.Q.astype(np.float32, copy=False), polar_coord)  # DICE-D embedding for `num`

        if self.norm == "l2":
            n = float(np.linalg.norm(dice))
            if n > 0:
                dice = dice / n

        return dice.astype(np.float32, copy=False)