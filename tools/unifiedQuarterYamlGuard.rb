#!/usr/bin/env ruby
# Strict declarative YAML guard. This is not a host config installer.
require "psych"
require "json"
root = File.expand_path("..", __dir__)
data = Psych.safe_load(File.read(File.join(root,"infra/unified-quarters/operating-profiles.yaml")), permitted_classes: [], permitted_symbols: [], aliases: false)
canon = JSON.parse(File.read(File.join(root,"doctrine/unifiedGoddessOrchestraV1.json")))
def ck(name, truth)
  abort("YAML_RED_#{name}") unless truth
end
ck("schema", data["schema"] == "luhmOs.unifiedQuarterProfiles.v1")
ck("law", data["source"] == "doctrine/unifiedGoddessOrchestraV1.json")
ck("stop", data["deployment"] == "DENY" && data["crownStatus"] == "STOP" && data["runtimeAgents"] == 0)
ck("npm", data["npm"] == {
  "role" => "DEVELOPER_ORCHESTRATION_ONLY",
  "private" => true,
  "androidRuntime" => false,
  "remoteProductionRuntime" => false,
  "installScriptsAllowed" => false,
  "publishAllowed" => false
})
ck("rhythm", data["beats"] == canon["fourBeats"])
ck("composition", data["composition"] == canon["composition"])
ck("quarters", data["quarters"].keys == canon["quarters"])
settings = {
  "local" => %w[automaticHardwarePermissions rootRequired runtimeNode],
  "remote" => %w[automaticInfrastructureDeployment publicSqlPort],
  "studio" => %w[automaticMediaCapture cloudGpuAssumed],
  "company" => %w[automaticPublish signingSecretsInRepo]
}
settings.each do |quarter, keys|
  ck("no_#{quarter}_automatic_mutation", keys.all? {|key| data["quarters"][quarter][key] == false })
end
ck("vendor_core", data["vendorReduction"]["core"] == canon["toolchain"]["vendorSelection"]["core"])
ck("vendor_optional", data["vendorReduction"]["optional"] == canon["toolchain"]["vendorSelection"]["optional"])
ck("vendor_safety", %w[autoDownloadThirdPartyCode duplicateProxyRequired duplicateBrowserRendererRequired].all? {|k| data["vendorReduction"][k] == false})
puts JSON.generate({schema:"luhmOs.unifiedQuarterYamlAudit.v1",quarterCount:4,beats:4,compositions:4,status:"SOURCE_YAML_GREEN",crown:"STOP"})
