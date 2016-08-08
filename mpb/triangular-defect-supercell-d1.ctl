(set! default-material (make dielectric (epsilon 2.4)))

(set! geometry-lattice (make lattice (size 8 4 no-size)
                         (basis1 (/ (sqrt 3) 2) 0.5)
                         (basis2 (/ (sqrt 3) 2) -0.5)))

(set! geometry (list (make cylinder
                       (center 0 0 0) (radius 0.25) (height infinity)
                       (material (make dielectric (epsilon 12.96))))))

(set! geometry (geometric-objects-lattice-duplicates geometry))

(set! geometry (append geometry 
                      (list (make cylinder (center 1 -1 0) 
                                  (radius 0.68) (height infinity)
                                  (material (make dielectric (epsilon 12.96)))))))

(set! geometry (append geometry 
                      (list (make cylinder (center 0 1 0) 
                                  (radius 0.68) (height infinity)
                                  (material (make dielectric (epsilon 12.96)))))))

(set! k-points (list (vector3 0 0 0)          ; Gamma
                     (vector3 0 0.5 0)        ; M
                     (vector3 (/ -3) (/ 3) 0) ; K
                     (vector3 0 0 0)))        ; Gamma
(set! k-points (interpolate 10 k-points))

;(set! k-points (list (vector3 (/ -3) (/ 3) 0))) ; K

(set! resolution 32)

(set! num-bands 12)
(set! target-freq (/ (+ 0.229 0.307) 2))
(set! tolerance 1e-8)

(run-tm (output-at-kpoint (vector3 (/ -3) (/ 3) 0)
                          fix-efield-phase output-efield-z))


(run-tm (output-at-kpoint (vector3 0 0.5 0)
                          fix-efield-phase output-efield-z))