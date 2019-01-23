<template>
	<div>
		<div id="dice-tools">
			<h3>Stats</h3>
			<h4>First Five</h4>
			<table class="stats" cellpadding="0" cellspacing="0"><tbody>
				<tr>
					<th>Magic Cost:</th>
					<td>
						<ol class="costs" v-if="firstFiveMagicCost">
							<li v-for="cost of firstFiveMagicCost" class="cost">
								<span v-if="isArray(cost)" class="parallel-costs">
									<span v-for="splitCost of cost" class="cost">
										<card-codes :content="splitCost"></card-codes>
									</span>
								</span>
								<card-codes v-else :content="cost"></card-codes>
							</li>
						</ol>
						<span v-else class="muted">--</span>
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
			<!-- TODO: add stats for things like:
			* Recurring effect dice costs
			* Average costs (magic and dice) for hands, taking into account the FF (and maybe recurring effect costs)
			* Average per-round dice recursion?
			
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
							[<ol class="costs">
								<li v-for="cost of magicCosts(phoenixborn, true)" class="cost">
									<span v-if="isArray(cost)" class="parallel-costs">
										<span v-for="splitCost of cost" class="cost">
											<card-codes :content="splitCost"></card-codes>
										</span>
									</span>
									<card-codes v-else :content="cost"></card-codes>
								</li>
							</ol>]
							<span class="dice-count">({{ diceCount(phoenixborn) }})</span>
						</div>
					</div>
				</li>
			</ul>
		</div>
		<div v-for="section of deckSections" :key="section.title" class="deck-section">
			<hr v-if="section.title == 'Conjuration Deck'">
			<h4>{{ section.title }}<span v-if="section.count" class="card-count"> ({{ section.count }})</span></h4>
			<ul>
				<li v-for="card of section.contents" :key="card.data.id">
					<div class="responsive-cols no-wrap">
						<div class="col" v-if="section.title !== 'Conjuration Deck'">
							<div class="btn-group">
								<button @click="toggleFirstFive(card.data.id)"
									class="btn btn-small"
									:class="{active: isInFirstFive(card.data.id)}"
									:disabled="isFirstFiveFull(card.data.id)"
									title="First Five"><i class="fa fa-hand-paper-o"></i></button
								><button @click="toggleEffectCost(card.data.id)"
									class="btn btn-small" title="Pay Effect Cost"
									:class="{active: isEffectCost(card.data.id)}"
									:disabled="!hasEffectCost(card.data)"
									><i class="fa fa-plus-square-o"></i></button
								>
							</div>
						</div>
						<div class="col-flex">
							{{ card.count }}&times; <card-link :card="card.data"></card-link>
							<span v-if="card.data.phoenixborn && section.title !== 'Conjuration Deck'"
									class="phoenixborn" :title="card.data.phoenixborn">
								({{ card.data.phoenixborn.split(' ')[0] }})
							</span>
						</div>
						<div class="col">
							<ol v-if="card.data.magicCost" class="costs">
								<li v-for="cost of magicCosts(card.data)" class="cost">
									<span v-if="isArray(cost)" class="parallel-costs">
										<span v-for="splitCost of cost" class="cost">
											<card-codes :content="splitCost"></card-codes>
										</span>
									</span>
									<card-codes v-else :content="cost"></card-codes>
								</li>
							</ol>
							<span v-if="card.data.effectMagicCost">
								[<ol class="costs">
									<li v-for="cost of magicCosts(card.data, true)" class="cost">
										<span v-if="isArray(cost)" class="parallel-costs">
											<span v-for="splitCost of cost" class="cost">
												<card-codes :content="splitCost"></card-codes>
											</span>
										</span>
										<card-codes v-else :content="cost"></card-codes>
									</li>
								</ol>]
							</span>
							<span class="dice-count" title="Dice Cost">({{ diceCount(card.data) }})</span>
						</div>
					</div>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import {includes, isArray} from 'lodash'
	import {globals} from 'app/utils'
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'
	
	function sortDiceTypes(a, b) {
		const aIsBasic = a === 'basic'
		const bIsBasic = b === 'basic'
		if (aIsBasic && !bIsBasic) {
			return 1
		}
		if (!aIsBasic && bIsBasic) {
			return -1
		}
		if (aIsBasic && bIsBasic) {
			return 0
		}
		const aIsSplit = includes(a, '/')
		const bIsSplit = includes(b, '/')
		if (aIsSplit && !bIsSplit) {
			return 1
		}
		if (!aIsSplit && bIsSplit) {
			return -1
		}
		if (aIsSplit && bIsSplit) {
			const aSplit = a.split(' / ')
			const bSplit = b.split(' / ')
			if (aSplit[0] === bSplit[0]) {
				return sortDiceTypes(aSplit[1], bSplit[1])
			}
			return sortDiceTypes(aSplit[0], bSplit[0])
		}
		const aPos = globals.diceData.indexOf(a)
		const bPos = globals.diceData.indexOf(b)
		if (aPos === bPos) {
			return 0
		}
		return aPos < bPos ? -1 : 1
	}
	
	function getSortedCostKeys(costObject) {
		let keys = Object.keys(costObject)
		keys.sort(sortDiceTypes)
		return keys
	}

	export default {
		props: ['viewOnly'],
		components: {
			'card-link': CardLink,
			'card-codes': CardCodes
		},
		computed: {
			deckSections () {
				return this.$store.getters.deckSections
			},
			totalCards () {
				return this.$store.getters.totalCards
			},
			firstFive () {
				return this.$store.getters.firstFive
			},
			effectCostCards () {
				return this.$store.getters.effectCostCards
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
				const cards = this.$store.getters.firstFive || []
				let costs = {}
				function extractCosts(costObject) {
					if (!costObject) {
						return
					}
					for (const key of Object.keys(costObject)) {
						costs[key] = costs[key] ? costs[key] + costObject[key] : costObject[key]
					}
				}
				for (const card of cards) {
					extractCosts(card.magicCost)
					if (this.isEffectCost(card.id)) {
						extractCosts(card.effectMagicCost)
					}
				}
				if (includes(this.$store.state.deck.effect_costs, this.phoenixborn.id)) {
					extractCosts(this.phoenixborn.effectMagicCost)
				}
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
			},
			firstFiveDiceCount () {
				const cards = this.$store.getters.firstFive || []
				let cost = 0
				for (const card of cards) {
					cost = cost + this.diceCount(card)
				}
				if (includes(this.$store.state.deck.effect_costs, this.phoenixborn.id)) {
					cost = cost + this.diceCount(this.phoenixborn)
				}
				return cost
			},
		},
		methods: {
			isArray,
			magicCosts (data, returnEffectCost) {
				if ((!returnEffectCost && !data.magicCost) || (returnEffectCost && !data.effectMagicCost)) {
					return []
				}
				const costObject = !returnEffectCost ? data.magicCost : data.effectMagicCost
				let costs = []
				const keys = getSortedCostKeys(costObject)
				for (const key of keys) {
					const dice = key.split(' / ')
					let finalCosts = []
					let firstIteration = true
					for (const cost of dice) {
						if (firstIteration) {
							finalCosts.push([costObject[key], ' [[', cost, ']]'].join(''))
							firstIteration = false
						} else {
							finalCosts.push(['[[', cost, ']]'].join(''))
						}
					}
					if (finalCosts.length > 1) {
						costs.push(finalCosts)
					} else {
						costs.push(finalCosts[0])
					}
				}
				return costs
			},
			diceCount (data) {
				let total = 0
				if (data.magicCost) {
					for (const value of Object.values(data.magicCost)) {
						total += value
					}
				}
				if (data.effectMagicCost && (this.isEffectCost(data.id) || (!data.magicCost && data.diceRecursion !== 0))) {
					for (const value of Object.values(data.effectMagicCost)) {
						total += value
					}
				}
				const recursion = data.diceRecursion || 0
				return total - recursion
			},
			hasEffectCost (data) {
				return !!data.effectMagicCost
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
