library(shinyWidgets)
library(tidyverse)
library(reticulate)
library(DT)
library(data.table)
reticulate::virtualenv_create(envname = "python_environment", python= "python3")
reticulate::virtualenv_install("python_environment", packages =c('pandas','catboost'))
reticulate:: py_discover_config()
# reticulate::use_virtualenv("python_environment",required = TRUE)
# boxing = read.csv(file="https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/visuals.csv",header=TRUE)
boxing <- readRDS('fullboxingdataset.RDS')
#reading model
p <- import("pandas")
cat_model <- p$read_pickle("catmodelsummary.pkl")
ui <- function(){
  addResourcePath("www","www")
  tagList(
    shinyUI(
      fluidPage(setBackgroundImage(src = "www/mayweather2.png"),
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
                       actionButton("goButton","Start Predictions")),
                hr(),
                column(offset=3,width=6,
                       DTOutput("predictions"))
      ) 
    )
  )}

server <- function(input,output){
  output$Names <- renderUI({
    req(input$dropdown)
    df <- boxing %>% filter(division %in% input$dropdown)
    selectInput("names","Boxer A",choices = df$name)
  })
  output$boxerA <- renderUI({
    tags$img(src=paste("www/",boxing[boxing$name == input$names, "global_id"],".jpg",sep=""),width=150)
  })
  output$Opponent <- renderUI({
    req(input$dropdown)
    df <- boxing %>% filter(division %in% input$dropdown)
    df <- df %>% filter(!name %in% input$names)
    selectInput("names2","Opponent",choices = df$name)
  })
  output$opppic <- renderUI({
    tags$img(src=paste("www/",boxing[boxing$name == input$names2, "global_id"],".jpg",sep=""),width=150)
  })
  
  
  observeEvent(input$goButton, {
    
    output$predictions <- renderDataTable({
      df1 <- boxing %>% filter(name %in% input$names)
      df2 <- boxing %>% filter(name %in% input$names2)
      df2$opp_loss <- df2$Loss.KO + df2$Loss.Other
      df2$opp_win <- df2$Win.KO + df2$Win.Other
      df1 <- df1 %>% select(Win.KO,Loss.Other,Loss.KO,Win.Other,KO.ratio,KnockedOut.ratio,Draw)
      df2 <- df2 %>% select(last6,KO.ratio,Win.Other,Win.KO,opp_loss,Loss.Other,opp_win,Loss.KO)
      setnames(df1,c("Win.KO","Loss.Other","Loss.KO","Win.Other","KO.ratio","KnockedOut.ratio"),c("winKO","lossOther","lossKO","winOther","KOratio","Knockedoutratio"))
      setnames(df2,c("last6","KO.ratio","Win.Other","Win.KO","Loss.Other","Loss.KO"), c("opp_last6","oppKOratio","opp_winOther","opp_winKO","opp_lossOther","opp_lossKO"))
      preds <- df1[,c("winKO","lossOther","lossKO","winOther","KOratio","Knockedoutratio","Draw")]
      preds2 <- df2[,c("opp_last6","oppKOratio","opp_winOther","opp_winKO","opp_loss","opp_lossOther","opp_win","opp_lossKO")]
      preds3 <- bind_cols(preds,preds2)
      df <- data.frame(probs = round(cat_model$predict_proba(preds3)*100,2))
      names(df)[1] <- "Draw"
      names(df)[2] <- "Loss"
      names(df)[3] <- "Win"
      #custom table
      datatable(df, container = htmltools::withTags(table(tableHeader(df))),options = list(pageLength=1,dom='tip'), rownames = FALSE, class = 'cell-border stripe')
    })
  })
}
shinyApp(ui = ui, server = server)


