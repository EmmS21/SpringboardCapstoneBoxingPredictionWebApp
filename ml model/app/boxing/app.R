library(shiny)
library(shinyWidgets)
library(tidyverse)
library(reticulate)
# boxing = read.csv(file="https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/visuals.csv",header=TRUE)
boxing <- readRDS('boxingdata3.rds')
boxing <- boxing[!is.na(boxing$name), ]
#reading model
p <- import("pandas")
cat_model <- p$read_pickle("catmodel.pkl")
ui <- shinyUI(
  fluidPage(setBackgroundImage(src = "mayweather2.png"),
    headerPanel(fluidRow(
      column(offset = 5, width=5,
             h2("Boxing Prediction App")),
      column(offset = 3, width = 7,
             h5("Welcome to Emmanuel's boxing prediction app. Using this app you can get the probability of a fight ending in a given way. The model used to derive these predictions uses data extracted before the 23rd of November 2019. Any updates to the data will be shown here. Without further ado, let's get ready to rumble!"))
    )),
    fluidRow(column(offset = 5, width = 2,align="center",
             titlePanel(h5(selectInput("dropdown","Select Boxer Weights",choices=unique(boxing$division)))))),
    fluidRow(column(offset = 3, width=3,
                    wellPanel(
                      fluidRow(
                        uiOutput("Names"),
                        uiOutput("boxerA")))),
             column(width = 3, align="right",
                    wellPanel(style = "height:300px",
                              fluidRow(
                                uiOutput("Opponent"),
                                uiOutput("opppic")
                              )))),
    hr(),
    column(offset=5,width = 8,
           actionButton("gobutton","Predict"),
           dataTableOutput("predictions")),
    hr(),
    column(offset=5,width = 5, 
           uiOutput("boxergifs"))
  ) 
)

server <- function(input,output){
  output$Names <- renderUI({
    req(input$dropdown)
    df <- boxing %>% filter(division %in% input$dropdown)
    selectInput("names","Boxer A",choices = df$name)
  })
  output$boxerA <- renderUI({
    tags$img(src=paste(boxing[boxing$name == input$names, "global_id"],".jpg",sep=""),width=150)
  })
  output$Opponent <- renderUI({
    req(input$dropdown)
    df <- boxing %>% filter(division %in% input$dropdown)
    selectInput("names2","Opponent",choices = df$name)
  })
  output$opppic <- renderUI({
    tags$img(src=paste(boxing[boxing$name == input$names2, "global_id"],".jpg",sep=""),width=150)
  })
  output$predictions <- renderDataTable({
    cat_model$predict(input$names,input$names2)
  })
  output$boxergifs <- renderUI({
    img(src=paste(boxing[boxing$name == input$names, "global_id"],".gif",sep=""),width=250)
  })
}
shinyApp(ui = ui, server = server)

