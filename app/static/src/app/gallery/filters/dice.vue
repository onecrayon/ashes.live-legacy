<template>
	<div class="btn-group">
		<button @click="toggleDiceLogic"
			class="btn btn-all" :class="{active: isDiceLogicActive }">{{ diceLogicText }}:</button
		><button @click="toggleDie('basic')"
			class="btn phg-basic-magic" :class="{active: isDieActive('basic') }"
			:disabled="isBasicDisabled" title="Basic"></button
		><button @click="toggleDie('ceremonial')"
			class="btn phg-ceremonial-power" :class="{active: isDieActive('ceremonial') }"
			title="Ceremonial"></button
		><button @click="toggleDie('charm')"
			class="btn phg-charm-power" :class="{active: isDieActive('charm') }"
			title="Charm"></button
		><button @click="toggleDie('illusion')"
			class="btn phg-illusion-power" :class="{active: isDieActive('illusion') }"
			title="Illusion"></button
		><button @click="toggleDie('natural')"
			class="btn phg-natural-power" :class="{active: isDieActive('natural') }"
			title="Natural"></button
		><button @click="toggleDie('divine')"
			class="btn phg-divine-power" :class="{active: isDieActive('divine') }"
			:disabled="!isShowingRelease(5)" title="Divine">D</button
		><button @click="toggleDie('sympathy')"
			class="btn phg-sympathy-power" :class="{active: isDieActive('sympathy') }"
			:disabled="!isShowingRelease(6)" title="Sympathy"></button>
	</div>
</template>

<script>
	import {includes} from 'lodash'
	
	export default {
		computed: {
			diceLogicText () {
				return this.$store.state.filters.diceLogic == 'or' ? 'Any' : 'All'
			},
			isDiceLogicActive () {
				return this.$store.state.filters.diceLogic == 'and'
			},
			isBasicDisabled () {
				return this.$store.state.filters.diceLogic == 'and'
			}
		},
		methods: {
			toggleDiceLogic () {
				this.$store.commit('toggleDiceLogic')
				this.$store.commit('filterCards')
			},
			toggleDie (die) {
				this.$store.commit('toggleDieFilter', die)
				this.$store.commit('filterCards')
			},
			isDieActive (die) {
				return includes(this.$store.state.filters.dice || [], die)
			},
			isShowingRelease (releaseNumber) {
				return includes(this.$store.state.filters.releases, releaseNumber)
			}
		}
	}
</script>

