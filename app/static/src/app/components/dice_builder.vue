<template>
	<div>
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
								<button class="btn btn-small" title="First Five" disabled><i class="fa fa-hand-paper-o"></i></button
								><button class="btn btn-small" title="Recurring"><i class="fa fa-refresh"></i></button
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
								><button class="btn btn-small" title="Recurring"
									:disabled="!canRecur(card.data)"
									><i class="fa fa-refresh"></i></button
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
							<span class="dice-count">({{ diceCount(card.data) }})</span>
						</div>
					</div>
				</li>
			</ul>
		</div>
		<!-- TODO: add stats for things like:
		* First Five "thunder number"/dice cost
		* Recurring dice costs
		* Average costs (magic and dice) for hands, taking into account the FF (and maybe recurring cards)
		* Average per-round dice recursion?
		
		Tool ideas:
		* Example randomized draw tool (with magic/dice cost output?)
		* Clear all recurring and FF toggles
		* Add PB ability to the very top of the list (and make it selectable as a recurring cost)?
		-->
	</div>
</template>

<script>
	import {includes, isArray} from 'lodash'
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'

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
			phoenixborn () {
				return this.$store.getters.phoenixborn
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
				for (const key of Object.keys(costObject)) {
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
				if (data.effectMagicCost) {
					for (const value of Object.values(data.effectMagicCost)) {
						total += value
					}
				}
				const recursion = data.diceRecursion || 0
				return total - recursion
			},
			canRecur (data) {
				if (includes(['Action Spell', 'Reaction Spell'], data.type)) {
					return false
				}
				return !!data.effectMagicCost
			},
			toggleFirstFive (cardId) {
				this.$store.commit('toggleFirstFive', cardId)
			},
			isInFirstFive (cardId) {
				return this.$store.state.deck.first_five.indexOf(cardId) > -1
			},
			isFirstFiveFull (cardId) {
				if (this.$store.state.deck.first_five.indexOf(cardId) > -1) {
					return false
				}
				return this.$store.state.deck.first_five.length === 5
			}
		}
	}
</script>
