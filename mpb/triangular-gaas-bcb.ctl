; a triangular lattice of GaAs pillars in BCB medium

(set! num-bands 8)

(set! geometry-lattice (make lattice (size 1 1 no-size)
                         (basis1 (/ (sqrt 3) 2) 0.5)
                         (basis2 (/ (sqrt 3) 2) -0.5)))
			 
(set! geometry (list (make cylinder
                       (center 0 0 0) (radius 0.25) (height infinity)
                       (material (make dielectric (epsilon 12.96))))))

(set! default-material (make dielectric (epsilon 2.4)))

(set! k-points (list (vector3 0 0 0)          ; Gamma
                     (vector3 0 0.5 0)        ; M
                     (vector3 (/ -3) (/ 3) 0) ; K
                     (vector3 0 0 0)))        ; Gamma
(set! k-points (interpolate 10 k-points))

(set! resolution 32)

(run-tm)