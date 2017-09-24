<<template>
	<div class="form-field">
		<input v-on:input="triggerFilter" type="text" placeholder="Filter by name or text...">
	</div>
</template>

<script>
	import {debounce} from 'lodash'

	export default {
		methods: {
			triggerFilter: debounce(function (event) {
				let search = event.target.value || null
				this.$store.commit('setSearch', search)
				this.$store.commit('filterCards')
			}, 400)
		}
	}
</script>

