# ADR-001 - Portfolio Manager

## Estado
Aprobado

## Contexto
JEMBA necesita un componente que decida qué oportunidades merecen usar capital disponible. El SignalEngine propone señales, el RankingEngine ordena oportunidades, pero el PortfolioManager decide qué activos pasan al RiskEngine.

## Decisión
El PortfolioManager será responsable de evaluar candidatos usando restricciones independientes.

## Entradas
- symbol
- score
- confidence
- signal
- liquidity
- spread
- volatility
- correlation
- portfolio_state

## Salidas
- approved
- rejected
- allocation
- rejection_reason

## Restricciones iniciales
- CapitalConstraint
- ExposureConstraint
- CorrelationConstraint

## Consecuencia
El PortfolioManager no tendrá reglas internas gigantes. Las reglas vivirán como constraints independientes para que el sistema crezca sin convertirse en sopa de ifs, esa exquisitez culinaria del software mal cuidado.
