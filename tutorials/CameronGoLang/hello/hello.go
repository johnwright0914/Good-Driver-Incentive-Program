package main //decalre a main package (group functions of all files in same directory)

import (
	"fmt"

	"rsc.io/quote/v4"
) //import package with text formatin, printing, etc.
//import pkg.go.dev modeule
//Go vscode extension delete unsued imports on attempted save

func main() {
	fmt.Println(quote.Go())
}

//run with "go run ."
