# Guía de datos demográficos en research

*UiX · Última actualización: abril 2026*

## Por qué estandarizar

Capturar edad, género, ubicación y ocupación con los mismos criterios hace que los datos sean claros, comparables y confiables entre equipos y estudios, y que los hallazgos se puedan cruzar y reutilizar. También ayuda a manejar con cuidado los datos sensibles o personales.

**Desde mayo 2026** todas las investigaciones deben recopilar cuatro datos: **edad, género, estado/residencia y profesión/ocupación**.

---

## 1. Edad

**Rangos (por generación)**

| Generación | Rango |
|---|---|
| Centennials (Gen Z) | 18-30 años |
| Millennials | 31-45 años |
| Gen X | 46-60 años |
| Boomers | 61+ años |

**Pregunta**
- Base: ¿En qué rango de edad te encuentras?
- Con tono adaptado, por ejemplo: "Antes de empezar, ¿cuántos años tienes?"

**Respuesta única:** 18-30 · 31-45 · 46-60 · 61+

**Reglas**
- Ordena los rangos de menor a mayor.
- Puedes cambiar el tono de la pregunta, pero **no** los rangos de respuesta.

**Si tu proyecto es para un grupo de edad específico**, puedes subdividir sin romper la división generacional base:

| Base | Específica |
|---|---|
| 18-30 | 18-24 · 25-30 |
| 31-45 | 31-45 |
| 46-60 | 46-54 · 55-60 |
| 61+ | 61+ |

**Por qué por generación.** La edad cronológica cambia con el tiempo (alguien de 18 años en 2022 es Gen Z; en 2030 un joven de 18 será de otra generación). La generación es un identificador fijo, así que mantiene los datos consistentes y comparables entre estudios. Además, la adopción de tecnología depende de cuándo nació cada persona.

**Qué nos facilita**
1. Rangos de edad estandarizados.
2. Segmentación consistente en el tiempo.
3. Comparar estudios históricos sin ambigüedad.

---

## 2. Género

**Categorías:** hablamos de género, no de sexo.

**Pregunta:** ¿Con qué género te identificas?

**Respuesta única:** Mujer · Hombre · No binario · Otro · Prefiero no decirlo

**Reglas**
- Incluye siempre los 3 géneros reconocidos (mujer, hombre, no binario). La identidad puede cambiar con el tiempo.
- Agrega "Otro" para validar cualquier identidad de género.
- Agrega "Prefiero no decirlo" para quienes no se sientan cómodos respondiendo.

**A considerar.** Puedes omitir la pregunta en Maze **solo si** tienes el dato desde el reclutamiento, pero **debes** registrarlo en el CVS que se sube al Data Analyst. Si la muestra es pequeña (por ejemplo, 8-10 usuarios en entrevistas, pruebas de usabilidad moderada o focus group), puedes preguntarlo de forma directa o pedirlo en el reclutamiento.

**Por qué incluir "no binario".** El género es más complejo que el estatus social, legal y las expectativas de la sociedad. No todas las personas se identifican con su sexo, y esa identidad se refleja igual en formas conductuales y cognitivas.

**Qué nos facilita**
1. Estandarizar la variable de comportamientos, experiencias y necesidades de usuarios específicos.
2. Comparar análisis entre estudios.
3. Contextualizar preferencias, deseabilidad e interés en un producto.

---

## 3. Estado / Residencia

**Zonas de México:** Norte · Centro-norte · Centro · Sur

**Pregunta**
- Base: ¿En qué lugar radicas actualmente?
- Con tono adaptado, por ejemplo: ¿En qué región de México vives?

**Respuesta única**
- **Norte:** Baja California, Chihuahua, Coahuila, Nuevo León, Sonora, Tamaulipas
- **Centro-norte:** Baja California Sur, Durango, Nayarit, Sinaloa, Zacatecas, Jalisco, Aguascalientes, Colima, Michoacán, San Luis Potosí
- **Centro:** CDMX, Edo. México, Guanajuato, Hidalgo, Morelos, Puebla, Querétaro, Tlaxcala
- **Sur:** Campeche, Chiapas, Guerrero, Oaxaca, Quintana Roo, Tabasco, Veracruz, Yucatán

**Reglas**
- Ordena de zona norte a zona sur.
- Puedes cambiar el tono de la pregunta, pero no los reactivos.
- Si tu estudio es en un estado específico, omite esta pregunta.

**A considerar.** Puedes omitirla en Maze **solo si** tienes la información precisa de dónde son tus usuarios reclutados, pero **debes** registrarla en el CVS que se sube al Data Analyst.

**¿Y si todos mis usuarios son del mismo estado o municipio?** Profundizar en la geografía debe responder una necesidad de negocio o de diseño del producto. Pregúntalo solo si el estudio lo justifica; si no, no lo preguntes. Si todos pertenecen al mismo estado o municipio, registra la información en el CVS que se sube al Data Analyst.

**Cuándo aplica**
- El cliente solicita conocer la perspectiva de distintas localidades.
- El MVP se lanzará en un estado específico.
- La hipótesis depende del contexto territorial.

Pregúntalo con opción múltiple de 1 elección.

**Por qué regiones y no pregunta abierta o lista completa.** Permite identificar comportamientos regionales sin ensuciar la muestra con variaciones en las respuestas (caso de un campo abierto) y baja la carga cognitiva al evitar la lista de los 32 estados.

**Qué nos facilita**
1. Estandarizar la variable geográfica.
2. Comparar estudios entre sí.
3. Contextualizar problemas de usabilidad.

**Nota.** La región influye en el acceso, uso y comprensión de productos digitales: infraestructura tecnológica, conectividad, nivel socioeconómico, alfabetización digital, patrones de consumo y referentes culturales. La clasificación coincide con la usada por Banxico, INEGI y la AMAI.

---

## 4. Profesión / Ocupación

**Taxonomía:** depende del **usuario final** del producto. La ocupación debe servir para explicar comportamientos observados, no para describir al usuario.

**Principios para preguntar bien**
1. Pregunta por rol, no por título.
2. Relaciona la ocupación con el tipo de producto.
3. Trabaja con opciones múltiples.
4. Pon roles específicos solo si el producto lo requiere.
5. Evita tecnicismos que el usuario no conozca.

### Producto para usuarios diversos (cualquiera puede acceder)

- Base: ¿Cuál es tu ocupación actual?
- Tono adaptado: ¿A qué te dedicas?

**Respuesta única:** Estudiante · Empleado(a) · Trabajador(a) independiente · Dedicado(a) al hogar · Pensionado(a) · Prefiero no decirlo

### Producto para usuarios específicos (solo para un grupo)

Ejemplo, una plataforma SAC (Servicio de Atención al Cliente):
- Base: ¿Cuál es tu ocupación actual?
- Tono adaptado: ¿Cuál es tu rol?

**Respuesta única:** Regional · Gerente · Administrador · Asesor · Consultor

Ejemplo, una plataforma de gestión para un colegio, con las mismas preguntas:

**Respuesta en opción múltiple:** Director · Maestro(a) · Alumno(a) · Administrador(a) · Supervisor(a)

**Reglas**
- Personaliza la ocupación según el tipo de producto.
- Con roles, ordénalos del mayor rango al menor.
- Si el producto es para usuarios específicos, todos los estudios deben usar la misma taxonomía.

**A considerar.** Puedes omitirla en Maze **solo si** tienes la ocupación de los usuarios reclutados, pero **debes** registrarla en el CVS que se sube al Data Analyst.

**Por qué ocupación y no profesión.** Según las prácticas de Nielsen Norman Group, pedimos información demográfica relevante; la profesión es un elemento que puede no ser relevante para todos los productos, sobre todo los específicos a un rubro en particular.

**Qué nos facilita**
1. Estandarizar la variable de comportamientos, experiencias y necesidades de usuarios específicos.
2. Comparar estudios del mismo producto.
3. Entender que el rol u ocupación de la persona dicta su modelo mental.

**Nota.** La clasificación coincide con la Encuesta Nacional de Ocupación y Empleo (ENOE) del INEGI: población ocupada (empleados, trabajadores independientes) y población no económicamente activa (estudiantes, amas/amos de casa y jubilados/pensionados).

---

## Referencias

- **Edad:** Pew Research Center y McCrindle Research (rangos generacionales); *Usability for Older Adults: Challenges and Changes* (Lexie Kane, 2019); *Defining generations: Where Millennials end and Generation Z begins* (Michael Dimock, 2019); Center for Generational Kinetics; Beresford Research.
- **Género:** Nielsen Norman Group; Bold Insight (*Design for all*); SurveyMonkey (*What does demographic data include?*).
- **Estado/Residencia:** Banxico, INEGI y AMAI; modelo NSE México; reporte de economías regionales; informe de movilidad social en México.
- **Ocupación:** ENOE del INEGI; Nielsen Norman Group.

*(Los enlaces originales están en el PNG; no pude copiarlos desde la imagen.)*
