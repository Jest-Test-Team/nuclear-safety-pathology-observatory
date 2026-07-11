import * as pulumi from "@pulumi/pulumi";
import { local } from "@pulumi/command";
import * as path from "path";

/**
 * Pulumi stack for OCI Neo.
 *
 * Terraform under infra/terraform remains the infrastructure source of truth.
 * This stack:
 * 1. Carries release image tags for the neo environment
 * 2. Runs `terraform validate` / `terraform plan` via @pulumi/command
 * 3. Optionally applies when autoApprove=true and skipApply=false
 */
const cfg = new pulumi.Config();
const environment = cfg.get("environment") || "neo";
const terraformDir = path.resolve(__dirname, cfg.get("terraformDir") || "../terraform");
const varFile = cfg.get("varFile") || "environments/neo.tfvars";

const apiImage = cfg.require("apiImage");
const webImage = cfg.require("webImage");
const pipelineImage = cfg.require("pipelineImage");

const autoApprove = cfg.getBoolean("autoApprove") ?? false;
const skipApply = cfg.getBoolean("skipApply") ?? true;

const tfVarFlags = [
  `-var=api_image=${apiImage}`,
  `-var=web_image=${webImage}`,
  `-var=pipeline_image=${pipelineImage}`,
  `-var-file=${varFile}`,
].join(" ");

const env = {
  TF_IN_AUTOMATION: "1",
  TF_INPUT: "0",
};

const init = new local.Command("terraform-init", {
  dir: terraformDir,
  create: "terraform init -input=false",
  update: "terraform init -input=false",
  environment: env,
  triggers: [apiImage, webImage, pipelineImage, environment],
});

const validate = new local.Command(
  "terraform-validate",
  {
    dir: terraformDir,
    create: "terraform validate",
    update: "terraform validate",
    environment: env,
    triggers: [apiImage, webImage, pipelineImage],
  },
  { dependsOn: [init] },
);

const plan = new local.Command(
  "terraform-plan",
  {
    dir: terraformDir,
    create: `terraform plan -input=false -out=tfplan ${tfVarFlags}`,
    update: `terraform plan -input=false -out=tfplan ${tfVarFlags}`,
    environment: env,
    triggers: [apiImage, webImage, pipelineImage],
  },
  { dependsOn: [validate] },
);

const apply = new local.Command(
  "terraform-apply",
  {
    dir: terraformDir,
    create: skipApply
      ? "echo 'skipApply=true; not applying'"
      : autoApprove
        ? "terraform apply -input=false -auto-approve tfplan"
        : "terraform apply -input=false tfplan",
    update: skipApply
      ? "echo 'skipApply=true; not applying'"
      : autoApprove
        ? "terraform apply -input=false -auto-approve tfplan"
        : "terraform apply -input=false tfplan",
    environment: env,
    triggers: [apiImage, webImage, pipelineImage, String(skipApply), String(autoApprove)],
  },
  { dependsOn: [plan] },
);

export const stackEnvironment = environment;
export const terraformDirectory = terraformDir;
export const plannedImages = { apiImage, webImage, pipelineImage };
export const validateStdout = validate.stdout;
export const planStdout = plan.stdout;
export const applyStdout = apply.stdout;
