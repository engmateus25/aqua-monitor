# Etapa 2 e 3: Design Analógico do SAR ADC

Esta etapa documenta o cálculo teórico dos componentes analógicos (O DAC e o Comparador).

## 1. Dimensionamento do DAC de Capacitores (Charge-Redistribution)

Para um ADC de 4-bits, a matriz capacitiva possui a seguinte distribuição de pesos binários:
- MSB (Bit 3): $C_3 = 8 \cdot C_0$
- Bit 2: $C_2 = 4 \cdot C_0$
- Bit 1: $C_1 = 2 \cdot C_0$
- LSB (Bit 0): $C_0 = 1 \cdot C_0$
- Terminação: $C_{term} = 1 \cdot C_0$

**Total de Capacitância ($C_{tot}$):** 
$$ C_{tot} = 8C_0 + 4C_0 + 2C_0 + 1C_0 + 1C_0 = 16 \cdot C_0 $$

### Cálculo do Capacitor Unitário ($C_0$)
O valor mínimo do capacitor unitário é limitado pelo ruído térmico ($kT/C$) para que o ruído não mascare o LSB.
A tensão do ruído térmico RMS é $v_{n,rms} = \sqrt{\frac{kT}{C_{tot}}}$.
Para evitar erros de quantização, queremos que $v_{n,rms} < \frac{V_{LSB}}{2}$.

Assumindo $V_{REF} = 1.8V$:
$$ V_{LSB} = \frac{1.8}{2^4} = 112.5 \text{ mV} $$
Portanto, o ruído precisa ser $< 56.25 \text{ mV}$.

Isso resulta em um limite teórico de capacitância minúsculo (na casa dos attofarads). No entanto, o **limitante real para projetos acadêmicos** é a capacitância parasita e o "matching" (casamento) das regras de design do layout (DRC). 

**Valor Escolhido para $C_0$:**
Para uma tecnologia de 180nm, capacitores Metal-Insulator-Metal (MIM) menores que $5 \mu m \times 5 \mu m$ sofrem com grande variação de borda (fringe capacitance).
Vamos adotar um capacitor unitário conservador de:
$$ C_0 = 100 \text{ fF} $$

- $C_{MSB} = 800 \text{ fF}$
- $C_{tot} = 1.6 \text{ pF}$ (Excelente para rápida acomodação RC sem consumir muita área).

## 2. O Comparador Analógico

O comparador precisa ter um ganho suficiente para resolver $\frac{V_{LSB}}{2} \approx 56 \text{ mV}$ para um nível lógico digital seguro (0V ou 1.8V).
Isso exige um ganho mínimo ($A_{min}$):
$$ A_{min} = \frac{V_{DD}}{\frac{V_{LSB}}{2}} = \frac{1.8V}{0.056V} = 32 \text{ V/V} \text{ (aprox. 30 dB)} $$

Como 30 dB é um requisito de ganho muito baixo, não precisaremos de um amplificador super complexo. 

**Arquitetura Sugerida:**
- **Op-Amp de Malha Aberta de 2 Estágios:** 
  1. *Estágio de Entrada:* Par diferencial PMOS com carga ativa NMOS (para permitir entrada em tensões próximas ao terra).
  2. *Estágio de Saída:* Inversor CMOS de alto ganho (Common Source).
- *Nota:* Sem capacitor de compensação (Miller), pois o comparador não tem malha de realimentação (queremos que ele chaveie o mais rápido possível e sature nos trilhos).

## 3. Próximo Passo
Desenhar o esquemático do comparador no simulador de circuitos (ex: LTspice ou NGspice) e extrair a curva de transferência.
