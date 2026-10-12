$taskFolder = $PSScriptRoot
$rows = Get-ChildItem -LiteralPath (Join-Path $taskFolder 'data\course-data') -File | ForEach-Object {
    $acl = Get-Acl -LiteralPath $_.FullName
    $rules = $acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])
    $everyone = @($rules | Where-Object { $_.IdentityReference.Value -eq 'S-1-1-0' -and $_.AccessControlType -eq 'Allow' })
    [pscustomobject]@{
        File = $_.Name
        InheritanceEnabled = -not $acl.AreAccessRulesProtected
        Rules = $rules.Count
        EveryoneAllowRules = $everyone.Count
    }
}
$rows | Export-Csv -LiteralPath (Join-Path $taskFolder 'local_acl.csv') -NoTypeInformation -Encoding utf8
$rows | Format-Table
