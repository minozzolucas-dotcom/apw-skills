# Farejador de coordenadas

Procedimento do passo 3. Este é o passo mais perigoso da skill — é onde se produz uma coordenada errada com aparência de certa. A regra que protege contra isso: **classifique a pista, seja honesto sobre o nível, nunca finja precisão que não existe.**

## Por que isso importa

O formulário "New Lead" abre, no fluxo normal, a partir de um clique no mapa de satélite — Lat/Long vêm do clique. A skill não tem esse clique; ela tem documentos. Documentos de site de telecom raramente trazem coordenada. O que eles trazem é endereço, ou — pior — memorial descritivo por confrontações.

Se a skill entrega um número de 6 casas decimais para algo que ela na verdade chutou, o Lucas cria o PIN no lugar errado e só descobre no campo. Por isso: três níveis, sempre rotulados.

## Nível ALTA — coordenada explícita no documento

O documento traz latitude/longitude. Formatos possíveis:
- Decimal: `-4.814786, -39.543692`
- Graus/minutos/segundos: `4°48'53"S 39°32'37"W` → converta para decimal.

No Brasil a latitude é negativa (Sul) e a longitude é negativa (Oeste). Faça uma checagem de sanidade: a coordenada cai dentro do município citado? Se cair, use direto. Se não cair, trate como divergência e pergunte ao Lucas.

## Nível MÉDIA — endereço geocodificável

Não há lat/long, mas há um endereço real: rodovia + km + bairro + município, ou rua + número + cidade. Exemplos: "BR-020, sentido Canindé, km 13, Cacimba Nova, Madalena/CE".

Procedimento:
1. Monte a string de endereço mais completa possível juntando todos os documentos.
2. Geocodifique. (Use o melhor recurso disponível no ambiente para transformar endereço em coordenada. Não invente a coordenada de cabeça.)
3. Devolva o ponto **com a margem de erro honesta**: referência de rodovia + km geocodifica num raio de centenas de metros a alguns km, não em metros.
4. Diga ao Lucas, explicitamente: "coordenada estimada por geocodificação do endereço, precisão ~X. Abre no satélite e confirma a posição da torre antes de criar o PIN."

## Nível BAIXA — só memorial descritivo

O documento só tem descrição por confrontações: "à margem nascente do Riacho Santa Catarina, extremando ao nascente com águas do Choró e ao poente com o leito do Riacho, 200 braças". Isso é um memorial cartorial antigo. **Não tem azimute, não tem coordenada, não tem ponto de amarração com GPS.**

Não tente triangular rios e divisas para gerar um ponto. Ninguém — humano ou IA — produz coordenada confiável a partir disso. Tentar é o erro que esta skill existe para evitar.

O que fazer:
1. Identifique o distrito/localidade mais específico que o documento permita (ex.: distrito de Cacimba Nova).
2. Devolva o **centroide desse distrito/município** como ponto de partida.
3. Rotule sem ambiguidade: "isto NÃO é a localização da torre. É o centro da região. Serve só para você abrir o satélite ali e procurar a estrutura da torre visualmente — o padrão de fundação aparece bem em imagem de satélite."
4. Sugira ao Lucas as pistas visuais que o documento deu para a busca no satélite: proximidade de rodovia, de rio, de cruzamento.

## Divergência de município

Se dois documentos discordam do município (contrato diz um, alvará/endereço dos proprietários diz outro), isso é comum em imóvel rural cortado pela divisa municipal. **Não escolha em silêncio.** Apresente os dois, diga de onde veio cada um, e pergunte ao Lucas qual usar — ou se ele quer confirmar no satélite antes. A divergência também vai registrada no Description do Lead.

## Saída do farejador

O farejador entrega sempre: (1) lat/long propostas, (2) o nível — ALTA / MÉDIA / BAIXA, (3) a frase de instrução correspondente ao nível, (4) divergências, se houver. Nunca entrega só o número.
