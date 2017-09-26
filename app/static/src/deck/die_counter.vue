<template>
	<div class="input-group">
		<div class="form-field">
			<input v-model.number="diceCount" type="number" min="0" step="1"
				:max="maxCount" @input="validateInput">
		</div>
		<button @click.prevent="incrementCount" class="btn btn-die"
			:class="dieType" :disabled="isDisabled">
			<span :class="['phg-' + dieType + '-power']"></span>
		</button>
	</div>
</template>

<script>
	export default {
		props: ['dieType'],
		computed: {
			diceCount: {
				get () {
					return this.$store.state.deck.dice[this.dieType]
				},
				set (value) {
					if (value > this.maxCount) {
						return
					}
					this.$store.commit('setDieCount', {die: this.dieType, count: value})
				}
			},
			maxCount () {
				return 10 - this.$store.getters.totalDice + this.diceCount
			},
			isDisabled () {
				return this.diceCount >= this.maxCount
			}
		},
		methods: {
			// LEFT OFF: need to test and see if this dual-validation actually works
			validateInput (event) {
				const el = event.target
				const value = parseInt(el.value) || 0
				if (value > this.maxCount) {
					el.value = this.diceCount
				}
			},
			incrementCount () {
				this.diceCount = this.diceCount + 1
			}
		}
	}
</script>

