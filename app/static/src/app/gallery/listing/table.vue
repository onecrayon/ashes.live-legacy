<template>
	<table class="tabular-listing" cellspacing="0" cellpadding="0">
		<tbody>
			<tr v-if="!listing.length">
				<td :colspan="numColumns" class="no-results">
					<h2>No cards found</h2>
					<p><button @click="resetFilters" class="btn btn-primary">Clear filters</button></p>
				</td>
			</tr>
			<tr v-for="card of listing" :key="card.id">
				<td v-if="numColumns === 5" class="qty-col">
					<qty-buttons :card="card" classes="btn-small"></qty-buttons>
				</td>
				<td class="type-col" :title="card.type">
					<i class="fa" :class="typeToFontAwesome(card.type)" aria-hidden="true"></i>
				</td>
				<td class="name-col">
					<card-link :card="card"></card-link>
					<span v-if="card.phoenixborn" class="phoenixborn" :title="card.phoenixborn">
						({{ card.phoenixborn.split(' ')[0] }})
					</span>
				</td>
				<td class="stats-col">
					<span v-if="hasStatline(card)" class="muted">
						<span v-if="card.attack !== undefined" class="attack">{{ card.attack }}</span>
						<span v-else>&ndash;</span> /
						<span v-if="card.life !== undefined" class="life">{{ card.life }}</span>
						<span v-else>&ndash;</span> /
						<span v-if="card.recover !== undefined" class="recover">{{ card.recover }}</span>
						<span v-else>&ndash;</span>
					</span>
					<card-link v-else-if="card.conjurations" :card="card.conjurations[0]">
						<i class="fa" :class="typeToFontAwesome('summon')"></i>
					</card-link>
				</td>
				<td class="costs-col">
					<ol v-if="card.cost" class="costs">
						<li v-for="cost of card.cost" class="cost">
							<span v-if="isArray(cost)" class="parallel-costs">
								<span v-for="splitCost of cost" class="cost">
									<card-codes :content="splitCost"></card-codes>
								</span>
							</span>
							<card-codes v-else :content="cost"></card-codes>
						</li>
					</ol>
					<span v-else-if="card.copies" class="muted">--</span>
				</td>
			</tr>
		</tbody>
	</table>
</template>

<script>
	import {isArray, startsWith} from 'lodash'
	import {globals, typeToFontAwesome} from 'app/utils'
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'
	import QtyButtons from './qty_buttons.vue'
	
	export default {
		components: {
			'card-link': CardLink,
			'qty-buttons': QtyButtons,
			'card-codes': CardCodes
		},
		computed: {
			listing () {
				return this.$store.state.listing
			},
			numColumns () {
				return globals.galleryOnly ? 4 : 5
			}
		},
		methods: {
			isArray,
			startsWith,
			typeToFontAwesome,
			hasStatline (card) {
				return card.attack !== undefined ||
					card.life !== undefined ||
					card.recover !== undefined
			},
			resetFilters () {
				this.$store.commit('resetFilters')
				this.$store.commit('filterCards')
			}
		}
	}
</script>
