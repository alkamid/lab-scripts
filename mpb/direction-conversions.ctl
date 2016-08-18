;in this script, I calculate different conversions between reciprocal
;and real-space lattices.

;Define the triangular lattice

(set! geometry-lattice (make lattice (size 1 1 no-size)
                          (basis1 1 0)
                          (basis2 0.5 (/ (sqrt 3) 2))))

;Simply display lattice vectors in cartesian coordinates

(display "Lattice vectors in cartesian coords:\n")
(display (lattice->cartesian (vector3 1 0 0)))
(display "\n")
(display (lattice->cartesian (vector3 0 1 0)))
(display "\n")

;What are the reciprocal lattice vectors?
(display "Reciprocal lattice vectors in cartesian coords:\n")
(display (reciprocal->cartesian (vector3 1 0 0)))
(display "\n")
(display (reciprocal->cartesian (vector3 0 1 0)))
(display "\n")

;What is the direction of M point in real space?
(display "M in reciprocal is (0, 0.5). What direction is it in cartesian coords?\n")
(display
	(reciprocal->cartesian (vector3 0 0.5 0))
)
(display "\n")

;Okay, so the direction of M is the same as the real y axis
;How about the real x axis?

(display "What is the direction in the first Brillouin zone of (1,0) in cartesian coords?\n")
(display
	(first-brillouin-zone
		(cartesian->reciprocal (vector3 1 0 0))
	)
)
(display "\n")

(quit)