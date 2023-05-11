package greetings //Declare greetings package, collect related functions

import (
	"errors"
	"fmt"
)

// implement hello function
// fuction name: Hello
// parameter: name, type string
// return type: string
func Hello(name string) (string, error) {
	if name == "" {
		return "", errors.New("empty name")
	}

	message := fmt.Sprintf("Hi, %v. Welcome!", name)
	return message, nil
}
