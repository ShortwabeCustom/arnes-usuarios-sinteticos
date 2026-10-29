# Piloto 2 · falla del instrumento (28/10/2026)

Bryan vio el SMS con el código (la ventana de observación funcionó) pero no pudo escribirlo: el campo real del código
es un `input` transparente (opacidad 0) encima de las 6 casillas, y el detector de elementos descartaba todo lo
transparente. El perfil escribió con «marca 0» (fuera de los elementos), reenvió dos veces y abandonó (22 pasos,
1.3 M tokens). El deslizamiento caía al centro de la pantalla, en el encabezado de la hoja de plazos, y no movía la
lista.

Corrección: un elemento transparente cuenta si es el que recibe el toque en su centro (`elementFromPoint`); deslizar
a 62 % de la altura. Validado sin modelo: el campo aparece y escribir el código lleva a «otpVerificado».

Señal que se repite con el piloto 1: confirma el plazo sin ver el total y no lee la letra chica del buró.
