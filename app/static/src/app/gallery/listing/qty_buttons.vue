<template>
	<div class="btn-group">
		<button class="btn btn-qty"
			:class="[isQty0Active ? 'active' : '', classes]"
			@click="setCardQty(card.id, 0)" v-html="zeroOutput || 0"></button
		><button class="btn btn-qty"
			:class="[isQty1Active ? 'active' : '', classes]"
			@click="setCardQty(card.id, 1)">1</button
		><button class="btn btn-qty"
			:class="[isQty2Active ? 'active' : '', classes]"
			@click="setCardQty(card.id, 2)">2</button
		><button class="btn btn-qty"
			:class="[isQty3Active ? 'active' : '', classes]"
			@click="setCardQty(card.id, 3)">3</button>
	</div>
</template>

<script>
	export default {
		props: ['card', 'classes', 'zeroOutput'],
		computed: {
			isQty0Active () {
				return !this.$store.state.deck.cards[this.card.id]
			},
			isQty1Active () {
				const count = this.$store.state.deck.cards[this.card.id]
				return count && count === 1
			},
			isQty2Active () {
				const count = this.$store.state.deck.cards[this.card.id]
				return count && count === 2
			},
			isQty3Active () {
				const count = this.$store.state.deck.cards[this.card.id]
				return count && count === 3
			},
		},
		methods: {
			setCardQty (id, qty) {
				this.$store.commit('setCardQty', {id: id, qty: qty})
			}
		}
	}
</script>

