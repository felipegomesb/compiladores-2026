 {fibonacci}
 
inteiro: n
inteiro: a = 0
inteiro: b = 1
inteiro: c
inteiro: i = 2;

inteiro fibonacci (inteiro n)
	
	se n <= 1 então
	retorna n

	repita
		c = a + b
		a = b
		b = c
		i++
	até i <= n
	retorna b
fim
	
inteiro principal ()

		leia (n)
		leia (a)		
		leia (b)
		leia (c)
		leia (i)

escreva (fibonacci(n))
fim	

	