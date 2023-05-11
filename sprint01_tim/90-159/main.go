package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

type user struct {
	ID		string	`json:"id"`
	Name	string	`json:"name"`
}

var users = []user{
	{ID: "0001", Name: "Tim"},
	{ID: "0002", Name: "Lau"},
}

func listUsers(ctx *gin.Context) {
	ctx.IndentedJSON(http.StatusOK, users)
}

func addUser(ctx *gin.Context) {
	var newUser user 
	if err := ctx.BindJSON(&newUser); err != nil {
		return 
	}
	users = append(users, newUser)
	ctx.IndentedJSON(http.StatusCreated, newUser)
}

func getUserByID(ctx *gin.Context) {
	id := ctx.Param("id")
	for _, u := range users {
		if u.ID == id {
			ctx.IndentedJSON(http.StatusOK, u)
			return
		}
	}
	ctx.IndentedJSON(http.StatusNotFound, gin.H{"message": "user not found"})
}

func main() {
	router := gin.Default()
	router.GET("/users", listUsers)
	router.GET("/users/id", getUserByID)
	router.POST("/users", addUser)


	router.Run("localhost:8080")
}
