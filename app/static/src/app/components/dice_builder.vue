<template>
	<div>
		<div id="dice-tools">
			<h3>Stats</h3>
			<h4>Dice</h4>
			<table class="stats" cellpadding="0" cellspacing="0"><tbody>
				<tr>
					<th>Faces/Round:</th>
					<td>
						<div v-if="averageDiceRolls">
							<div v-for="stats of averageDiceRolls" :key="stats">
								<card-codes :content="stats"></card-codes>
							</div>
						</div>
						<span v-else class="muted">--</span>
					</td>
				</tr>
				<tr>
					<th>% For One:</th>
					<td>
						<card-codes v-if="powerProbability" :content="powerProbability"></card-codes>
						<span v-else class="muted">--</span>
					</td>
				</tr>
			</tbody></table>

			<h4>All Cards</h4>
			<table class="stats" cellpadding="0" cellspacing="0"><tbody>
				<tr>
					<th>Play Cost:</th>
					<td>
						<cost-list :costs="deckMagicCost" use-highlights></cost-list>
					</td>
				</tr>
				<tr>
					<th>Dice Required:</th>
					<td>
						<cost-list :costs="deckDiceRequired"></cost-list>
					</td>
				</tr>
				<tr>
					<th>Recursion:</th>
					<td>
						{{ maxDiceRecursion }} <span class="muted">dice returned</span>
					</td>
				</tr>
			</tbody></table>

			<h4>Spellboard</h4>
			<table class="stats" cellpadding="0" cellspacing="0"><tbody>
				<tr>
					<th>Base Cost:</th>
					<td>
						<cost-list :costs="spellboardEffectMinCost" use-highlights></cost-list>
					</td>
				</tr>
				<tr>
					<th>Max Cost:</th>
					<td>
						<cost-list :costs="spellboardEffectMaxCost" use-highlights></cost-list>
					</td>
				</tr>
			</tbody></table>

			<h4>First Five</h4>
			<table class="stats" cellpadding="0" cellspacing="0"><tbody>
				<tr>
					<th>Magic Cost:</th>
					<td>
						<cost-list :costs="firstFiveMagicCost" use-highlights></cost-list>
					</td>
				</tr>
				<tr>
					<th>Dice Required:</th>
					<td>
						<cost-list :costs="firstFiveDiceRequired"></cost-list>
					</td>
				</tr>
				<tr>
					<th>Dice Cost:</th>
					<td>{{ firstFiveDiceCount }}</td>
				</tr>
				<tr>
					<th>Cards:</th>
					<td>
						<span :class="{error: firstFiveTotalCards > firstFiveLimit}">{{ firstFiveTotalCards }}</span> <span class="muted">of {{ firstFiveLimit }} possible</span>
					</td>
				</tr>
			</tbody></table>
			<!--
			Tool ideas:
			* Example randomized draw tool (with magic/dice cost output?)
			* Clear all effect cost and FF toggles
			-->
		</div>
		<hr>
		<h3 class="responsive-cols no-wrap">
			<div class="col-flex">
				Cards
				<span class="card-count">
					(<span :class="{error: totalCards > 30}">{{ totalCards }}</span> / 30)
				</span>
			</div>
			<div class="col">
				<div class="btn-group compressed">
					<button class="btn btn-small" :class="{active: activeCost == 'magic'}"
						@click="activeCost = 'magic'" title="Magic Cost">Magic</button
					><button class="btn btn-small" :class="{active: activeCost == 'dice'}"
						@click="activeCost = 'dice'" title="Dice Required"
						>Dice</button
					>
				</div>
			</div>
		</h3>
		<div v-if="phoenixborn.effectMagicCost" class="deck-section">
			<ul>
				<li>
					<div class="responsive-cols no-wrap">
						<div class="col">
							<div class="btn-group">
								<button class="btn btn-small" title="First Five"
									disabled><i class="fa fa-hand-paper-o"></i></button
								><button @click="toggleEffectCost(phoenixborn.id)"
									class="btn btn-small"
									:class="{active: isEffectCost(phoenixborn.id)}"
									title="Pay Effect Cost"
									><i class="fa fa-plus-square-o"></i></button
								>
							</div>
						</div>
						<div class="col-flex">
							<card-link :card="phoenixborn"><em>{{ phoenixborn.text[0].name }}</em></card-link>
						</div>
						<div class="col">
							[<cost-list :costs="getCardCostOutput(phoenixborn, true)"></cost-list>] 
							<span class="dice-count">({{ diceCount(phoenixborn) }})</span>
						</div>
					</div>
				</li>
			</ul>
		</div>
		<div v-for="section of deckSections" :key="section.title" class="deck-section">
			<hr v-if="section.isConjurations">
			<h4>{{ section.title }}<span v-if="section.count" class="card-count"> ({{ section.count }})</span></h4>
			<ul>
				<li v-for="card of section.contents" :key="card.data.id">
					<div class="responsive-cols no-wrap">
						<div class="col">
							<div class="btn-group">
								<button @click="toggleFirstFive(card.data.id)"
									class="btn btn-small"
									:class="{active: isInFirstFive(card.data.id)}"
									:disabled="section.isConjurations || isFirstFiveFull(card.data.id)"
									title="First Five"><i class="fa fa-hand-paper-o"></i></button
								><button @click="toggleEffectCost(card.data.id)"
									class="btn btn-small" title="Pay Effect Cost"
									:class="{active: isEffectCost(card.data.id)}"
									:disabled="!isEffectCostActive(card.data)"
									><i class="fa fa-plus-square-o"></i></button
								>
							</div>
						</div>
						<div class="col-flex">
							{{ card.count }}&times; <card-link :card="card.data"></card-link>
							<span v-if="card.data.phoenixborn && !section.isConjurations"
									class="phoenixborn" :title="card.data.phoenixborn">
								({{ card.data.phoenixborn.split(' ')[0] }})
							</span>
						</div>
						<div class="col">
							<cost-list v-if="card.data.magicCost" :costs="getCardCostOutput(card.data)"></cost-list>
							<span v-if="card.data.effectMagicCost">
								[<cost-list :costs="getCardCostOutput(card.data, true)"></cost-list>]
							</span>
							<span class="dice-count" title="Dice Cost">({{ diceCount(card.data) }}<span v-if="card.data.effectRepeats && isEffectCost(card.data.id)">+</span>)</span>
						</div>
					</div>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import {concat, filter, includes, round} from 'lodash'
	import {globals} from 'app/utils'
	import CardLink from 'app/components/card_link.vue'
	import CostList from 'app/components/cost_list.vue'
	import CardCodes from 'app/components/card_codes.vue'
	
	function costToDiceType(cost) {
		const splitCosts = cost.split(' / ')
		if (splitCosts.length > 1) {
			let types = []
			for (const splitCost of splitCosts) {
				types.push(splitCost.split(':')[0])
			}
			return types.join(' / ')
		}
		return splitCosts[0].split(':')[0]
	}
	
	function costToDiceFace(cost) {
		if (cost === 'basic') {
			return null
		}
		const data = cost.split(':')
		// Default to power face
		if (data.length !== 2) {
			return 'power'
		}
		return data[1]
	}
	
	function sortDiceTypes(a, b) {
		const aIsBasic = a === 'basic'
		const bIsBasic = b === 'basic'
		if (!aIsBasic && bIsBasic) return -1
		if (aIsBasic && bIsBasic) return 0
		if (aIsBasic && !bIsBasic) return 1
		const aIsSplit = includes(a, '/')
		const bIsSplit = includes(b, '/')
		if (!aIsSplit && bIsSplit) return -1
		if (aIsSplit && bIsSplit) {
			const aSplit = a.split(' / ')
			const bSplit = b.split(' / ')
			if (costToDiceType(aSplit[0]) === costToDiceType(bSplit[0])) {
				return sortDiceTypes(aSplit[1], bSplit[1])
			}
			return sortDiceTypes(aSplit[0], bSplit[0])
		}
		if (aIsSplit && !bIsSplit) return 1
		const aPos = globals.diceData.indexOf(costToDiceType(a))
		const bPos = globals.diceData.indexOf(costToDiceType(b))
		if (aPos === bPos) {
			const aFace = costToDiceFace(a)
			const bFace = costToDiceFace(b)
			if (aFace === 'power' && bFace !== 'power' || (aFace === 'class' && !bFace)) {
				return -1
			}
			if (aFace === bFace) return 0
			else return 1
		}
		return aPos < bPos ? -1 : 1
	}
	
	function getSortedCostKeys(costObject) {
		let keys = Object.keys(costObject)
		keys.sort(sortDiceTypes)
		return keys
	}
	
	function extractDiceRequired(costs, costObject) {
		if (!costObject) {
			return
		}
		for (const key of Object.keys(costObject)) {
			const diceType = costToDiceType(key)
			costs[diceType] = costs[diceType] ? costs[diceType] + costObject[key] : costObject[key]
		}
	}
	
	function extractMagicCosts(costs, cards, returnEffectCost) {
		for (const card of cards) {
			const costObject = !returnEffectCost ? card.magicCost : card.effectMagicCost
			if (!costObject) continue
			for (const key of Object.keys(costObject)) {
				costs[key] = costs[key] ? costs[key] + costObject[key] : costObject[key]
			}
		}
	}
	
	function getFormattedCosts(costs) {
		let formattedCosts = []
		const keys = getSortedCostKeys(costs)
		for (const key of keys) {
			const dice = key.split(' / ')
			let finalCosts = []
			let firstIteration = true
			for (const cost of dice) {
				if (firstIteration) {
					finalCosts.push([costs[key], ' [[', cost, ']]'].join(''))
					firstIteration = false
				} else {
					finalCosts.push(['[[', cost, ']]'].join(''))
				}
			}
			if (finalCosts.length > 1) {
				formattedCosts.push(finalCosts)
			} else {
				formattedCosts.push(finalCosts[0])
			}
		}
		if (!formattedCosts.length) {
			return null
		}
		return formattedCosts
	}

	export default {
		props: ['viewOnly'],
		components: {
			'card-link': CardLink,
			'cost-list': CostList,
			'card-codes': CardCodes
		},
		data () {
			return {
				'activeCost': 'magic'
			}
		},
		computed: {
			deckSections () {
				return this.$store.getters.deckSections
			},
			totalCards () {
				return this.$store.getters.totalCards
			},
			phoenixborn () {
				return this.$store.getters.phoenixborn
			},
			firstFiveTotalCards () {
				return this.$store.state.deck.first_five.length
			},
			firstFiveLimit () {
				return this.$store.getters.firstFiveLimit
			},
			firstFiveMagicCost () {
				const cards = concat(
					this.$store.getters.firstFive || [],
					this.$store.getters.effectCostOnlyCards || []
				)
				let costs = {}
				extractMagicCosts(costs, cards)
				const effectCards = filter(cards, (card) => {
					return this.isEffectCost(card.id)
				})
				extractMagicCosts(costs, effectCards, true)
				return getFormattedCosts(costs)
			},
			firstFiveDiceRequired () {
				const cards = concat(
					this.$store.getters.firstFive || [],
					this.$store.getters.effectCostOnlyCards || []
				)
				let costs = {}
				for (const card of cards) {
					extractDiceRequired(costs, card.magicCost)
					if (this.isEffectCost(card.id)) {
						extractDiceRequired(costs, card.effectMagicCost)
					}
				}
				return getFormattedCosts(costs)
			},
			firstFiveDiceCount () {
				const cards = concat(
					this.$store.getters.firstFive || [],
					this.$store.getters.effectCostOnlyCards || []
				)
				let cost = 0
				let repeatingEffect = false
				for (const card of cards) {
					cost = cost + this.diceCount(card)
					if (card.effectRepeats) {
						repeatingEffect = true
					}
				}
				return cost + (repeatingEffect ? '+' : 0)
			},
			deckMagicCost () {
				const cards = this.$store.getters.allCards
				let costs = {}
				extractMagicCosts(costs, cards)
				return getFormattedCosts(costs)
			},
			deckDiceRequired () {
				const cards = this.$store.getters.allCards
				let costs = {}
				for (const card of cards) {
					extractDiceRequired(costs, card.magicCost)
				}
				return getFormattedCosts(costs)
			},
			maxDiceRecursion () {
				const cards = this.$store.getters.allCards
				let recursion = 0
				for (const card of cards) {
					recursion += card.diceRecursion || 0
				}
				return recursion
			},
			spellboardEffectMinCost () {
				const cards = []
				const usedIds = []
				for (const card of this.$store.getters.allCards) {
					if (card.type == 'Ready Spell' && !includes(usedIds, card.id)) {
						cards.push(card)
						usedIds.push(card.id)
					}
				}
				let costs = {}
				extractMagicCosts(costs, cards, true)
				return getFormattedCosts(costs)
			},
			spellboardEffectMaxCost () {
				const cards = filter(this.$store.getters.allCards, (card) => {
					return card.type == 'Ready Spell'
				})
				let costs = {}
				extractMagicCosts(costs, cards, true)
				return getFormattedCosts(costs)
			},
			averageDiceRolls () {
				const costs = []
				for (const dieType of getSortedCostKeys(this.$store.state.deck.dice)) {
					const numDice = this.$store.state.deck.dice[dieType]
					if (!numDice) continue
					costs.push(
						// 1/6 chance of a power face per die
						round(numDice / 6, 2) + ' [[' + dieType + ':power]] - ' +
						// 3/6 chance of a class face per die
						round(numDice / 2, 2) + ' [[' + dieType + ':class]]'
					)
				}
				if (!costs.length) return null
				return costs
			},
			powerProbability () {
				const costs = []
				for (const dieType of getSortedCostKeys(this.$store.state.deck.dice)) {
					const numDice = this.$store.state.deck.dice[dieType]
					if (!numDice) continue
					// 1/6 chance of a power face per die
					costs.push(
						round((1 - Math.pow(5/6, numDice)) * 100) + '% [[' + dieType + ':power]]'
					)
				}
				return costs.join(' - ')
			},
		},
		methods: {
			getCardCostOutput (data, returnEffectCost) {
				if ((!returnEffectCost && !data.magicCost) || (returnEffectCost && !data.effectMagicCost)) {
					return []
				}
				let costs = {}
				if (this.activeCost == 'magic') {
					extractMagicCosts(costs, [data], returnEffectCost)
				} else {
					const costObject = !returnEffectCost ? data.magicCost : data.effectMagicCost
					extractDiceRequired(costs, costObject)
				}
				return getFormattedCosts(costs)
			},
			diceCount (data) {
				let total = 0
				if (data.magicCost) {
					for (const value of Object.values(data.magicCost)) {
						total += value
					}
				}
				if (data.effectMagicCost && (this.isEffectCost(data.id) || (!data.magicCost && data.diceRecursion))) {
					for (const value of Object.values(data.effectMagicCost)) {
						total += value
					}
				}
				const recursion = data.diceRecursion || 0
				return total - recursion
			},
			isEffectCostActive (data) {
				return !!data.effectMagicCost && (
					this.isInFirstFive(data.id) ||
					includes(['Conjuration', 'Conjured Alteration Spell', 'Phoenixborn'], data.type)
				)
			},
			toggleFirstFive (cardId) {
				this.$store.commit('toggleFirstFive', cardId)
			},
			isInFirstFive (cardId) {
				return includes(this.$store.state.deck.first_five, cardId)
			},
			isFirstFiveFull (cardId) {
				// Always allow toggling if the card is already in the First Five
				if (this.isInFirstFive(cardId)) {
					return false
				}
				return this.$store.state.deck.first_five.length === this.$store.getters.firstFiveLimit
			},
			toggleEffectCost (cardId) {
				this.$store.commit('toggleEffectCost', cardId)
			},
			isEffectCost (cardId) {
				return includes(this.$store.state.deck.effect_costs, cardId)
			},
		}
	}
</script>
