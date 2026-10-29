# Piloto 1 · falla del instrumento (28/10/2026)

Bryan abandonó T1 en el código de verificación tras 22 pasos (1.3 M tokens). No es un hallazgo del producto:

- El SMS simulado con el código aparece unos segundos y se quita. El perfil tarda ≈ 20 s en decidir cada paso y la
  captura se tomaba 0.3 s después del toque, así que nunca lo vio. Una persona lo habría visto en su teléfono.
- «Esperar» no dejaba pasar tiempo real (la pantalla se asentaba en 0.3 s).
- «Desplazar» usaba la rueda del mouse, que en el celular emulado no movía la lista de plazos.

Corrección: ventana de observación de 3 s tras cada acción (el aviso queda en la captura), avisos que aparecieron y
se fueron se le cuentan al perfil, «esperar» = 5 s reales, desplazar = gesto táctil (CDP synthesizeScrollGesture).

Lo que sí sirve como señal (una sola sesión): Bryan confirmó el plazo sin ver el total («No veo cuánto pago en
total, pero con ese número me alcanza para decidir») y continuó sin leer la letra chica del buró.
