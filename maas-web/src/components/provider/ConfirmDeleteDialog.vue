<!--
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
-->

<template>
  <ConfirmDialog
    :model-value="modelValue"
    type="danger"
    :title="dialogTitle"
    :message="dialogMessage"
    :details="dialogDetails"
    confirm-text="删除"
    cancel-text="取消"
    loading-text="删除中..."
    :loading="loading"
    @update:model-value="$emit('update:modelValue', $event)"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import type { Provider } from '@/types/providerTypes'

interface Props {
  modelValue: boolean
  provider: Provider | null
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', provider: Provider): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<Emits>()

const dialogTitle = computed(() => '确认删除供应商')

const dialogMessage = computed(() => {
  if (!props.provider) return ''
  return `确定要删除供应商 "${props.provider.display_name}" 吗？此操作不可撤销。`
})

const dialogDetails = computed(() => {
  if (!props.provider) return ''
  return `供应商类型：${props.provider.provider_type}，状态：${props.provider.is_active ? '激活' : '停用'}`
})

const handleConfirm = () => {
  if (props.provider) {
    emit('confirm', props.provider)
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>